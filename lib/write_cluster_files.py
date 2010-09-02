import string
import os, sys
import numpy

#sys.path.append("lib")
import coord_conversion

################################################################################
#                                                                              #
#  This library contains all the functions creating the files used on the      #
#  calculation cluster. The functions related to the Create_Zindo.py file as   #
#  well as the Quantum_Sampling_Generation.py will be stored here.             #
#                                                                              #
################################################################################

# ******************************************************************************
#                       Functions related to Create_Zindo.py
# ******************************************************************************

def CreateXYZ(data, cell, project, filename_base, verb=2):
	""" Create the .xyz file containing the coordinates of all the atoms
		in the system.
	"""
	file = '%s%s%s.xyz' % (project.input_cluster, os.sep, filename_base)
	try:
		foutput = open(file, 'w')
	except:
		if verb>0:
			print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
		
	tmp = '%d %d\n' % (data.n_frame, len(project.molecules_to_analyze_full))
	for ii in project.molecules_to_analyze_full:
		tmp += '%d ' % (data.n_atom[ii])
	tmp += '\n'	
	foutput.writelines(tmp)
	tmp = ''
	
	for i in xrange(data.n_frame):
		tmp += 'frame %d\n' % (i)
		for ii in project.molecules_to_analyze_full:
			tmp += 'molecule %d\n' % (data.mol_number[i, ii])
			for iii in xrange(data.n_atom[ii]):
				tmp += '%4s %5d %12f %5d %15f %15f %15f\n'\
				% (data.symbol[i][ii][iii], data.atomic_number[i, ii, iii], data.atomic_mass[i, ii, iii], data.atomic_valence[i, ii, iii], data.x[i, ii, iii], data.y[i, ii, iii], data.z[i, ii, iii]) 
		if ( i%100 == 0 ):
			foutput.writelines(tmp)
			tmp = ''
			if verb > 3:
				print "[INFO] Writing frame %d in the file %s" % (i, file)
	
	foutput.write(tmp)
	foutput.close()
	
def CreateXYZ_MT(data, cell, project, filename_base, verb=2):
	""" Create the .xyz file containing the coordinates of all the atoms
		in the system.
	"""
	import multiprocessing
	
	file = '%s%s%s.xyz' % (project.input_cluster, os.sep, filename_base)
	try:
		foutput = open(file, 'w')
	except:
		if verb>0:
			print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
		
	tmp = '%d %d\n' % (data.n_frame, len(project.molecules_to_analyze_full))
	for ii in project.molecules_to_analyze_full:
		tmp += '%d ' % (data.n_atom[ii])
	tmp += '\n'	
	foutput.writelines(tmp)
	tmp = ''
	
	frame_0 = 0
	frame_1 = 20
	frame_2 = 40
	
	while frame_1 < data.n_frame and frame_2 < data.n_frame:
		ps = []
		
		parent_1, child_1 = multiprocessing.Pipe()
		parent_2, child_2 = multiprocessing.Pipe()

		p = multiprocessing.Process(target = CreateXYZ_MT_thread, args = (child_1, data, cell, project, frame_0, frame_1, verb))
		ps.append(p)
		p.start()

		p = multiprocessing.Process(target = CreateXYZ_MT_thread, args = (child_2, data, cell, project, frame_1, frame_2, verb))
		ps.append(p)
		p.start()
		
		res_thr1 = parent_1.recv()
		res_thr2 = parent_2.recv()
		
		for x in ps:
			p.join()
			
		foutput.writelines(res_thr1)
		foutput.writelines(res_thr2)
		
		if frame_0%100 == 0 and verb > 3:
			print "[INFO] Writing frame %d in the file %s" % (frame_0, file)
		
		frame_0 = frame_2
		frame_1 = frame_0 + 20
		frame_2 = frame_0 + 40
			
		
	tmp = ''	
	for i in xrange(frame_0, data.n_frame, 1):
		tmp += 'frame %d\n' % (i)
		for ii in project.molecules_to_analyze_full:
			tmp += 'molecule %d\n' % (data.mol_number[i, ii])
			for iii in xrange(data.n_atom[ii]):
				tmp += '%4s %5d %12f %5d %15f %15f %15f\n'\
				% (data.symbol[i][ii][iii], data.atomic_number[i, ii, iii], data.atomic_mass[i, ii, iii], data.atomic_valence[i, ii, iii], data.x[i, ii, iii], data.y[i, ii, iii], data.z[i, ii, iii]) 

	foutput.write(tmp)
				
	foutput.close()
	
def CreateXYZ_MT_thread(child, data, cell, project, frame_i, frame_f, verb=2):
	tmp = ''	
	for i in xrange(frame_i, frame_f, 1):
		tmp += 'frame %d\n' % (i)
		for ii in project.molecules_to_analyze_full:
			tmp += 'molecule %d\n' % (data.mol_number[i, ii])
			for iii in xrange(data.n_atom[ii]):
				tmp += '%4s %5d %12f %5d %15f %15f %15f\n'\
				% (data.symbol[i][ii][iii], data.atomic_number[i, ii, iii], data.atomic_mass[i, ii, iii], data.atomic_valence[i, ii, iii], data.x[i, ii, iii], data.y[i, ii, iii], data.z[i, ii, iii]) 

	child.send(tmp)
	child.close()

def CreateCELL(data, cell, project, filename_base):
	""" Create the .cell file containing the cell parameters related
		to the .xyz file.
	"""
	tmp = 'PBC %s' % (project.pbc_number)
	tmp += 'cutoff %f\n' % (project.cutoff)
	for i in xrange(data.n_frame):
		tmp += 'frame %d\n' % (i)
		tmp += '%f %f %f %f %f %f\n' % (cell.a[i], cell.b[i], cell.c[i], cell.alpha_deg[i], cell.beta_deg[i], cell.gamma_deg[i])
		tmp += '%.15f %.15f %.15f %.15f %.15f %.15f %.15f\n' % (cell.temp_alpha_cos[i], cell.temp_beta_sin[i], cell.temp_beta_cos[i], cell.temp_gamma_sin[i], cell.temp_gamma_cos[i], cell.temp_beta_term[i], cell.temp_gamma_term[i])

	file = '%s%s%s.cell' % (project.input_cluster, os.sep, filename_base)
	try:
		foutput = open(file, 'w')
	except:
		print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
	
	foutput.write(tmp)
	foutput.close()

def CreateCM(data, project, filename_base):
	""" Create the .cm file containing the center of masses of the molecules
		of the .xyz file.
	"""
	tmp = ''
	for i in xrange(data.n_frame):
		tmp += 'frame %d\n' % (i)
		for ii in project.molecules_to_analyze_full:
			if ii in project.molecules_for_J_full:
				a = 1
			else:
				a = 0
			tmp += 'molecule %d %d ' % (data.mol_number[i, ii], data.n_electrons[i, ii])
			tmp += '%.15f %.15f %.15f %d\n' % (data.CM_x[i, ii], data.CM_y[i, ii], data.CM_z[i, ii], a)

	file = '%s%s%s.cm' % (project.input_cluster, os.sep, filename_base)
	try:
		foutput = open(file, 'w')
	except:
		print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
	
	foutput.write(tmp)
	foutput.close()
	
def CreateZIN(project, filename_base):
	""" Create the .zin file containing information for sign calculation
	"""
	tmp = '%d %d %d %d %d \n' % (project.sign, project.coeff_H_lign, project.coeff_H_row, project.coeff_L_lign, project.coeff_L_row)

	file = '%s%s%s.zin' % (project.input_cluster, os.sep, filename_base)
	try:
		foutput = open(file, 'w')
	except:
		print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
	
	foutput.write(tmp)
	foutput.close()
	
def ScriptFileCreation(project):
	""" Create the script used to calculate the neighbors.
	"""
	tmp = ''
	tmp += '#!/bin/bash\n\n'
	tmp += 'DIR="%s"\n' % (project.dir_cluster)
	tmp += 'INPUT_DIR="%s"\n' % (project.input_dir_cluster)
	tmp += 'OUTPUT_DIR="%s"\n' % (project.output_dir_cluster)
	tmp += 'ZINDO_DIR="%s"\n' % (project.zindo_dir_cluster)
	if project.location_cluster == "joe":
		tmp += 'SCRATCH_DIR="%s"\n\n' % (project.scratch_dir_cluster)
	elif project.location_cluster == "lyra" or project.location_cluster == "adam":
		tmp += 'SCRATCH_DIR="$TMPDIR"\n\n' % (project.scratch_dir_cluster)
		#tmp += 'SCRATCH_DIR="\\%s"\n\n' % (project.scratch_dir_cluster)
	elif project.location_cluster == "lucky" or project.location_cluster == "william":
		tmp += 'SCRATCH_DIR="/scratch/"$PBS_JOBID""\n\n'
	else:
		print '[ERROR] Bad cluster location. Aborting...'
		sys.exit(1)

	tmp += 'if [[ -d $DIR ]]; then\n'
	tmp += '	cd $DIR\n'
	tmp += 'else\n'
	tmp += '	echo "The folder $DIR does not exist, but it is supposed to be the project directory. Aborting..."\n'
	tmp += '	exit\n'
	tmp += 'fi\n\n'

	tmp += 'mkdir -p $SCRATCH_DIR\n'
	tmp += 'mkdir -p $OUTPUT_DIR\n'
	tmp += 'mkdir -p $INPUT_DIR/ZINDO\n\n'

	tmp += 'cd $INPUT_DIR/MD\n'
	tmp += 'find . -name "*" | cpio -pd $SCRATCH_DIR\n'
	tmp += 'cp $DIR/CZ_input_zindo_mc* $SCRATCH_DIR\n'
	tmp += 'cd $SCRATCH_DIR\n\n'

	if project.location_cluster == "lyra" or project.location_cluster == "adam":
		tmp += '#pgcpp -fast -Minline=levels:10 CZ_input_zindo_mc.cpp\n'
		tmp += '#mv a.out CZ_input_zindo_mc\n\n'
	else:
		tmp += 'g++ CZ_input_zindo_mc.cpp -o CZ_input_zindo_mc -O2 -lm\n\n'

	tmp += 'for FILE in `find . -name "*.xyz"`\n'
	tmp += 'do\n'
	tmp += '	NAME=`echo $FILE | cut -d "." -f2 | cut -d "/" -f2`\n'
	tmp += '	mkdir -p $NAME\n\n'
	
	tmp += '	i=0\n'
	tmp += "	N_FRAME=`sed -n 1,1p $FILE | awk '{ print $1 }'`\n"
	tmp += '	while [ $i -lt $N_FRAME ]\n'
	tmp += '	do\n'
	tmp += '		mkdir -p $NAME/frame_$i\n'
	tmp += '		mkdir -p output/$NAME/frame_$i\n'
	tmp += '		(( i = $i+1 ))\n'
	tmp += '	done\n\n'

	tmp += '	./CZ_input_zindo_mc -I $NAME -i . -o output/$NAME -z $ZINDO_DIR -t zindo\n\n'
	
	tmp += '	i=0\n'
	tmp += '	while [ $i -lt $N_FRAME ]\n'
	tmp += '	do\n'
	tmp += '		tar cfz "$NAME"_frame_"$i".tar.gz $NAME/frame_$i\n'
	tmp += '		mv "$NAME"_frame_"$i".tar.gz $INPUT_DIR/ZINDO\n'
	tmp += '		rm -rf $NAME/frame_$i\n\n'
	
	tmp += '		cd output\n'
	tmp += '		tar cfz output_"$NAME"_frame_"$i"_DIST.tar.gz $NAME/frame_$i\n'
	tmp += '		mv output_"$NAME"_frame_"$i"_DIST.tar.gz $OUTPUT_DIR\n'
	tmp += '		rm -rf output/$NAME/frame_$i\n'
	tmp += '		cd $SCRATCH_DIR\n\n'
	
	tmp += '		(( i = $i+1 ))\n'
	tmp += '	done\n\n'	
	
	tmp += 'done\n\n'

	tmp += 'mv $SCRATCH_DIR/*.nb $INPUT_DIR/MD\n'
	tmp += 'rm -rf $SCRATCH_DIR\n'
	
	file = 'project%s%s%s01.file_creation.sh' % (os.sep, project.project_name, os.sep)
	try:
		foutput = open(file, 'w')
	except:
		print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
	
	foutput.write(tmp)
	foutput.close()
	
def ScriptFileCreationDirect(project):
	""" Create the script used to calculate the neighbors in interactive mode.
	"""
	tmp = ''
	tmp += '#!/bin/bash\n\n'
	tmp += 'DIR="%s"\n' % (project.dir_cluster)
	tmp += 'INPUT_DIR="%s"\n' % (project.input_dir_cluster)
	tmp += 'OUTPUT_DIR="%s"\n' % (project.output_dir_cluster)
	tmp += 'ZINDO_DIR="%s"\n\n' % (project.zindo_dir_cluster)

	tmp += 'if [[ -d $DIR ]]; then\n'
	tmp += '	cd $DIR\n'
	tmp += 'else\n'
	tmp += '	echo "The folder $DIR does not exist, but it is supposed to be the project directory. Aborting..."\n'
	tmp += '	exit\n'
	tmp += 'fi\n\n'

	tmp += 'mkdir -p $OUTPUT_DIR\n'
	tmp += 'mkdir -p $INPUT_DIR/ZINDO\n\n'

	tmp += 'cp CZ_input_zindo_mc* $INPUT_DIR/MD\n'
	tmp += 'cd $INPUT_DIR/MD\n\n'

	if project.location_cluster == "lyra" or project.location_cluster == "adam":
		tmp += '#module load common pgi\n'
		tmp += '#pgcpp -fast -Minline=levels:10 CZ_input_zindo_mc.cpp\n'
		tmp += '#mv a.out CZ_input_zindo_mc\n\n'
	else:
		tmp += 'g++ CZ_input_zindo_mc.cpp -o CZ_input_zindo_mc -O2 -lm\n\n'

	tmp += 'for FILE in `find . -name "*.xyz"`\n'
	tmp += 'do\n'
	tmp += '	cd $INPUT_DIR/MD\n'
	tmp += '	NAME=`echo $FILE | cut -d "." -f2 | cut -d "/" -f2`\n'
	tmp += '	echo "Currently analyzing file $NAME..."\n'
	tmp += '	mkdir -p $NAME\n\n'
	
	tmp += '	i=0\n'
	tmp += "	N_FRAME=`sed -n 1,1p $FILE | awk '{ print $1 }'`\n"
	tmp += '	while [ $i -lt $N_FRAME ]\n'
	tmp += '	do\n'
	tmp += '		mkdir -p $NAME/frame_$i\n'
	tmp += '		mkdir -p $OUTPUT_DIR/$NAME/frame_$i\n'
	tmp += '		(( i = $i+1 ))\n'
	tmp += '	done\n\n'

	tmp += '	./CZ_input_zindo_mc -I $NAME -i $INPUT_DIR/MD -o $OUTPUT_DIR/$NAME -z $ZINDO_DIR -t zindo\n\n'

	tmp += '	i=0\n'
	tmp += '	while [ $i -lt $N_FRAME ]\n'
	tmp += '	do\n'
	tmp += '		cd $INPUT_DIR/MD\n'
	tmp += '		tar cfz "$NAME"_frame_"$i".tar.gz $NAME/frame_$i\n'
	tmp += '		mv "$NAME"_frame_"$i".tar.gz $INPUT_DIR/ZINDO\n'
	tmp += '		rm -rf $NAME/frame_$i\n\n'
	
	tmp += '		cd $OUTPUT_DIR\n'
	tmp += '		tar cfz output_"$NAME"_frame_"$i"_DIST.tar.gz $NAME/frame_$i\n'
	tmp += '		rm -rf $OUTPUT_DIR/$NAME/frame_$i\n\n'
	
	tmp += '		(( i = $i+1 ))\n'
	tmp += '	done\n\n'
	tmp += '	rm -rf $OUTPUT_DIR/$NAME\n\n'	
	tmp += 'done\n\n'
	tmp += 'rm $INPUT_DIR/MD/CZ_input_zindo_mc*\n'
	
	file = 'project%s%s%s01.file_creation_direct.sh' % (os.sep, project.project_name, os.sep)
	try:
		foutput = open(file, 'w')
	except:
		print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
	
	foutput.write(tmp)
	foutput.close()

def ScriptFileCreationPBS(project):
	""" Create the .pbs file for the neighbor calculations.
	"""
	tmp = ''
	if project.location_cluster == "joe":
		tmp += '#!/bin/csh\n'
		tmp += '#PBS -q long\n' 
		tmp += '#PBS -l nodes=1:p4:ppn=1\n'
		tmp += '#PBS -A %s\n' % (project.username_cluster)
		tmp += '#PBS -M %s@averell.umh.ac.be\n' % (project.username_cluster)
		tmp += '#PBS -m ae\n'
		tmp += '#PBS -V\n\n'
	
	elif project.location_cluster == "lyra" or project.location_cluster == "adam":
		tmp += '#!/bin/bash\n\n'
		tmp += '#$ -j y\n'
		tmp += '#$ -cwd\n'
		tmp += '#$ -l vf=2G\n'
		tmp += '#$ -l h_cpu=600:00:00\n'
		tmp += '#$ -N %s\n' % (project.project_name)
		tmp += '#$ -m bea\n'
		tmp += '#$ -M nicolas.g.martinelli@gmail.com\n\n'
 
		tmp += 'module load common pgi\n\n'
		
	elif project.location_cluster == "lucky" or project.location_cluster == "william":
		tmp += '#!/bin/bash\n\n'
		tmp += '#PBS -l nodes=1:ppn=1,walltime=999:00:00,mem=1gb\n'
		tmp += '#PBS -M nicolas.g.martinelli@gmail.com\n'
		tmp += '#PBS -m ea\n\n'

	else:
		print '[ERROR] Bad cluster location. Aborting...'
		sys.exit(1)

	tmp += 'cd %s\n' % (project.dir_cluster)
	tmp += 'chmod +x 01.file_creation.sh\n'
	tmp += './01.file_creation.sh\n'

	file = 'project%s%s%s01.file_creation.pbs' % (os.sep, project.project_name, os.sep)
	try:
		foutput = open(file, 'w')
	except:
		print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
	
	foutput.write(tmp)
	foutput.close()

def ScriptZINDOLaunch(project):
	""" Create a bash script which will create the scripts (.pbs and .run files) needed 
		to run all the ZIND0 calculations.
	"""
	tmp = ''
	tmp += '#!/bin/bash\n\n'
	tmp += 'DIR="%s"\n' % (project.dir_cluster)
	tmp += 'INPUT_DIR="%s"\n' % (project.input_dir_cluster)
	tmp += 'OUTPUT_DIR="%s"\n' % (project.output_dir_cluster)
	tmp += 'ZINDO_DIR="%s"\n\n' % (project.zindo_dir_cluster)
	if project.location_cluster == "joe":
		tmp += 'SCRATCH_DIR="%s"\n\n' % (project.scratch_dir_cluster)
	elif project.location_cluster == "lyra" or project.location_cluster == "adam":
		tmp += 'SCRATCH_DIR="\\$TMPDIR"\n\n' % (project.scratch_dir_cluster)
		#tmp += 'SCRATCH_DIR="\\%s"\n\n' % (project.scratch_dir_cluster)
	elif project.location_cluster == "lucky" or project.location_cluster == "william":
		tmp += 'SCRATCH_DIR="/scratch/"\\$PBS_JOBID""\n\n'
	else:
		print '[ERROR] Bad cluster location. Aborting...'
		sys.exit(1)
		
	tmp += 'N_PBS=6\n\n'

	tmp += 'MakePBS(){\n'

	if project.location_cluster == "joe":
		tmp += '	echo "#!/bin/csh" 				> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#PBS -q long"				>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#PBS -l nodes=1:p4:ppn=1" 		>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#PBS -A `whoami`" 			>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#PBS -M `whoami`@averell.umh.ac.be" 		>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#PBS -m bae" 				>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#PBS -V" 					>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo " "					>> $DIR/zindo_$1.pbs\n'

	elif project.location_cluster == "lyra" or project.location_cluster == "adam":
		tmp += '	echo "#!/bin/bash"			>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#$ -j y"					>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#$ -cwd"					>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#$ -l vf=2G"				>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#$ -l h_cpu=600:00:00"		>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#$ -N %s_$1"		>> $DIR/zindo_$1.pbs\n' % (project.project_name)
		tmp += '	echo "#$ -m ea"		>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#$ -M nicolas.g.martinelli@gmail.com"		>> $DIR/zindo_$1.pbs\n'
 		tmp += '	echo " "					>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "module load common"			>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo " "					>> $DIR/zindo_$1.pbs\n'

	elif project.location_cluster == "lucky" or project.location_cluster == "william":
		tmp += '	echo "#!/bin/bash"			> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#PBS -l nodes=1:ppn=1,walltime=999:00:00,mem=1gb\"			>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#PBS -M nicolas.g.martinelli@gmail.com"			>> $DIR/zindo_$1.pbs\n'
		tmp += '	echo "#PBS -m ea"			>> $DIR/zindo_$1.pbs\n'
	
	else:
		print '[ERROR] Bad cluster location. Aborting...'
		sys.exit(1)
		
	tmp += '	echo "cd $DIR"					>> $DIR/zindo_$1.pbs\n'
	tmp += '	echo "chmod +x zindo_$1.run"			>> $DIR/zindo_$1.pbs\n'
	tmp += '	echo "./zindo_$1.run"				>> $DIR/zindo_$1.pbs\n'
	tmp += '}\n\n'

#	tmp += 'MakeRUN(){\n'
#	tmp += '	echo "#!/bin/bash" 				> $DIR/zindo_$1.run\n'
#	tmp += '	echo " "					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "mkdir -p $SCRATCH_DIR"			>> $DIR/zindo_$1.run\n'
#	tmp += '	echo " "					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "for x in \`cat $DIR/zindo_$1.dir\`"	>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "do"					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	cd $INPUT_DIR/ZINDO"			>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	cp --parents -R -f \$x $SCRATCH_DIR"	>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	cd $SCRATCH_DIR/\$x"			>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	for CMD in \`find . -name \'*.cmd\'\`"	>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	do"					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "		chmod +x \$CMD"			>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "		./\$CMD"			>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	done"					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	rm -rf $SCRATCH_DIR/\$x"		>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "done"					>> $DIR/zindo_$1.run\n\n'
#	tmp += '}\n\n'

#	tmp += 'MakeRUN(){\n'
#	tmp += '	echo "#!/bin/bash"								> $DIR/zindo_$1.run\n'
#	tmp += '	echo " "										>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "mkdir -p $SCRATCH_DIR"					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo " "										>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "for TAR in \`cat $DIR/zindo_$1.dir\`"		>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "do"										>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	cd $INPUT_DIR/ZINDO"					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	cp \$TAR $SCRATCH_DIR"					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	cd $SCRATCH_DIR"						>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	x=\`echo \$TAR | cut -d \"/\" -f2 | cut -d \".\" -f1\`"	>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	mkdir \$x ; mv \$TAR \$x ; cd \$x"		>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	tar xfz \$TAR"							>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	for FILE in \`find . -name \'*.*\'\`"		>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	do"										>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "		mv \$FILE ."					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	done"									>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	for CMD in \`find . -name \'*.cmd\'\`"	>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	do"										>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "		chmod +x \$CMD"					>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "		./\$CMD"						>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	done"									>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "	rm -rf $SCRATCH_DIR/\$x"				>> $DIR/zindo_$1.run\n'
#	tmp += '	echo "done"										>> $DIR/zindo_$1.run\n'

	tmp += 'MakeRUN(){\n'
	tmp += '	echo "#!/bin/bash" > $DIR/zindo_$1.run\n\n'
	tmp += '	echo " " >> $DIR/zindo_$1.run\n'
	
	tmp += '	echo "OUTPUT_DIR="%s"" >> $DIR/zindo_$1.run\n\n' % (project.output_dir_cluster)
	tmp += '	echo " " >> $DIR/zindo_$1.run\n'
	
	tmp += '	echo "mkdir -p $SCRATCH_DIR" >> $DIR/zindo_$1.run\n\n'
	tmp += '	echo " " >> $DIR/zindo_$1.run\n'
	
	tmp += '	echo "for TAR in \`cat $DIR/zindo_$1.dir\`" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "do" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	cd $INPUT_DIR/ZINDO" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	cp \$TAR $SCRATCH_DIR" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	cd $SCRATCH_DIR" >> $DIR/zindo_$1.run\n\n'
	tmp += '	echo " " >> $DIR/zindo_$1.run\n'
	
	tmp += '	echo "	PROJECT=\`echo \$TAR | awk -F \'/\' \'{print \$2}\' | awk -F \'_frame_\' \'{print \$1}\'\`" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	FRAME=\`echo \$TAR | awk -F \'_frame_\' \'{print \$2}\' | cut -d \'.\' -f1\`" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	mkdir -p \$PROJECT/frame_\$FRAME" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	mv \$TAR \$PROJECT/frame_\$FRAME" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	cd \$PROJECT/frame_\$FRAME" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	tar xfz \$TAR" >> $DIR/zindo_$1.run\n\n'
	tmp += '	echo " " >> $DIR/zindo_$1.run\n'
	
	tmp += '	echo "	for FILE in \`find . -name \'*.*\'\`" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	do" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "		mv \$FILE ." >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	done" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	for CMD in \`find . -name \'*.cmd\'\`" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	do" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "		chmod +x \$CMD" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "		./\$CMD" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	done" >> $DIR/zindo_$1.run\n\n'
	tmp += '	echo " " >> $DIR/zindo_$1.run\n'
	
	tmp += '	echo "	cd $SCRATCH_DIR" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	tar cfz output_\\"\$PROJECT\\"_frame_\\"\$FRAME\\"_J.tar.gz \$PROJECT/frame_\$FRAME/dimer_*_*.out \$PROJECT/frame_\$FRAME/molecule_*.coeff_*" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "	mv output_\\"\$PROJECT\\"_frame_\\"\$FRAME\\"_J.tar.gz \$OUTPUT_DIR" >> $DIR/zindo_$1.run\n\n'
	tmp += '	echo " " >> $DIR/zindo_$1.run\n'
	
	tmp += '	echo "	rm -rf \$PROJECT/frame_\$FRAME" >> $DIR/zindo_$1.run\n'
	tmp += '	echo "done" >> $DIR/zindo_$1.run\n'
	tmp += '}\n\n'
	
	tmp += 'i=1\n'
	tmp += 'j=1\n'
	tmp += 'k=0\n\n'

	tmp += 'cd $INPUT_DIR/ZINDO\n\n'

	tmp += 'find . -name "*frame*" > directories.tmp\n'
	tmp += 'N_DIR=`wc -l directories.tmp | awk \'{print $1}\'`\n'
	tmp += 'N_STEP=$(($N_DIR/$N_PBS + 1))\n'

	tmp += 'while [ $i -le $N_PBS ]\n'
	tmp += 'do\n\n'

	tmp += '	k=$(($j+$N_STEP))\n'
	tmp += '	MakePBS $i\n'
	tmp += '	MakeRUN $i\n'
	tmp += '	sed -n "$j","$k"p directories.tmp > $DIR/zindo_$i.dir\n\n'

	tmp += '	j=$(($k+1))\n'
	tmp += '	i=$(($i+1))\n\n'

	tmp += 'done\n\n'
	
	tmp += 'cd $DIR\n'
	tmp += 'for PBS in `ls zindo_*.pbs`\n'
	tmp += 'do\n'
	tmp += '	qsub $PBS\n'
	tmp += 'done\n'

	file = 'project%s%s%s02.launch_zindo.sh' % (os.sep, project.project_name, os.sep)
	try:
		foutput = open(file, 'w')
	except:
		print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
	
	foutput.write(tmp)
	foutput.close()
	
def ScriptZINDOCollectDirect(data, project):
	""" Create the script used to collect the transfer integrals values.
	"""
	
	a = data.n_electrons[0, 0]/2
	
	tmp = ''
	tmp += '#!/bin/bash\n\n'
	tmp += 'DIR="%s"\n' % (project.dir_cluster)
	tmp += 'INPUT_DIR="%s"\n' % (project.input_dir_cluster)
	tmp += 'OUTPUT_DIR="%s"\n\n' % (project.output_dir_cluster)
	tmp += 'RESULTS_DIR="%s"\n\n' % (project.results_dir_cluster)

	tmp += 'if [[ -d $DIR ]]; then\n'
	tmp += '	cd $DIR\n'
	tmp += 'else\n'
	tmp += '	echo "The folder $DIR does not exist, but it is supposed to be the project directory. Aborting..."\n'
	tmp += '	exit\n'
	tmp += 'fi\n\n'

	tmp += 'mkdir -p $RESULTS_DIR\n'
	tmp += 'g++ ZINDO_sign.cpp -O2 -lm -o $RESULTS_DIR/ZINDO_sign\n'
	tmp += 'g++ CZ_input_zindo_mc.cpp -O2 -lm -o $RESULTS_DIR/CZ_input_zindo_mc\n\n'

#	tmp += 'cd $INPUT_DIR/MD\n'
#	tmp += 'SYSTEM_LIST=`find . -maxdepth 1 -name "*.xyz" | awk -F \'\\\\\\\\.xyz\' \'{ print $1 }\' | awk -F \'\/\' \'{ print $2 }\'`\n\n'
#	tmp += 'SYSTEM_LIST=`find . -maxdepth 1 -name "*.xyz" | awk -F \'.xyz\' \'{ print $1 }\' | awk -F \'/\' \'{ print $2 }\'`\n\n'
	
	tmp += 'cd $OUTPUT_DIR\n'
	tmp += 'for x in `find . -maxdepth 1 -name "*J.tar.gz"`; do\n'
	tmp += '	tar xfz $x\n'
	tmp += 'done\n\n'

	tmp += "for SYSTEM in `find $INPUT_DIR/MD -maxdepth 1 -name '*.xyz' | awk -F 'input/MD/' '{print $2}' | cut -d '.' -f1`; do\n"
	tmp += '	if [[ -d $SYSTEM ]]; then\n'
	tmp += '		echo "Collecting results for system" $SYSTEM"..."\n'
	tmp += '		cd $SYSTEM\n'
	tmp += '		for FRAME in `find . -maxdepth 1 -name "*" | sort -t "_" -k 2 -g | awk -F \'/\' \'{ print $2 }\'`; do\n'
	tmp += '			if [[ -d $FRAME ]]; then\n'
	tmp += '				echo $FRAME\n'
	tmp += '				cd $FRAME\n'
	tmp += '				for x in `find . -maxdepth 1 -name "*.out"`; do\n'
	tmp += '					MOL_1=`echo $x | cut -d "_" -f2`\n'
	tmp += '					MOL_2=`echo $x | cut -d "_" -f3 | cut -d "." -f1`\n'
	tmp += '					J_H=`grep " i(1)%13d j(2)%13d" $x | awk \'{print $6}\'`\n' % (a, a)
	tmp += '					J_L=`grep " i(1)%13d j(2)%13d" $x | awk \'{print $6}\'`\n' % (a+1, a+1)
	tmp += '					N=`echo $FRAME | cut -d "_" -f2`\n\n'
	
	tmp += '					if [[ $J_H == \'\' ]]; then\n'
	tmp += '						echo "Problem at frame" $N "between molecules" $MOL_1 "and" $MOL_2 .\n'
	tmp += '						J_H="0.0"\n'
	tmp += '						J_L="0.0"\n'
	tmp += '					fi\n\n'
					
	tmp += '					if [[ -f molecule_"$MOL_1".coeff_h ]]; then\n'
	tmp += '						H_1=`cat molecule_"$MOL_1".coeff_h`\n'
	tmp += '					else\n'
	tmp += '						H_1="1.0"\n'
	tmp += '					fi\n\n'
					
	tmp += '					if [[ -f molecule_"$MOL_2".coeff_h ]]; then\n'
	tmp += '						H_2=`cat molecule_"$MOL_2".coeff_h`\n'
	tmp += '					else\n'
	tmp += '						H_2="1.0"\n'
	tmp += '					fi\n\n'

	tmp += '					if [[ -f molecule_"$MOL_1".coeff_l ]]; then\n'
	tmp += '						L_1=`cat molecule_"$MOL_1".coeff_l`\n'
	tmp += '					else\n'
	tmp += '						L_1="1.0"\n'
	tmp += '					fi\n\n'

	tmp += '					if [[ -f molecule_"$MOL_2".coeff_l ]]; then\n'
	tmp += '						L_2=`cat molecule_"$MOL_2".coeff_l`\n'
	tmp += '					else\n'
	tmp += '						L_2="1.0"\n'
	tmp += '					fi\n'
	tmp += '					a=`echo $x | cut -d "/" -f2`\n'
	tmp += '					echo $N $J_H $H_1 $H_2 $J_L $L_1 $L_2 >> "$DIR"/results/"$SYSTEM"_"$a"\n'
	tmp += '				done\n'
	tmp += '				cd ..\n'
	tmp += '			fi\n'
	tmp += '		done\n'
	tmp += '		cd ..\n'
	tmp += '	fi\n'
	tmp += 'done\n\n'

	tmp += 'echo "Collection of results done! Now calculating the sign (if possible)..."\n'
	tmp += 'cd $RESULTS_DIR\n'
	tmp += 'for x in `find . -maxdepth 1 -name "*.out"`; do\n'
	tmp += '	mol1=`echo $x | awk -F \'_dimer_\' \'{ print $2 }\' | awk -F \'.out\' \'{ print $1 }\' | cut -d "_" -f1`\n'
	tmp += '	mol2=`echo $x | awk -F \'_dimer_\' \'{ print $2 }\' | awk -F \'.out\' \'{ print $1 }\' | cut -d "_" -f2`\n'
	tmp += '	n_frame=`wc -l $x | awk \'{ print $1 }\'`\n'
	tmp += '	echo $n_frame $mol1 $mol2 > "$x".sign\n'
	tmp += '	./ZINDO_sign -n $n_frame -f $x >> "$x".sign\n'
	tmp += 'done\n\n'

	tmp += 'echo "Creating Monte-Carlo input files..."\n'
	tmp += 'cd $RESULTS_DIR\n'
	tmp += "for SYSTEM in `find $INPUT_DIR/MD -maxdepth 1 -name '*.xyz' | awk -F 'input/MD/' '{print $2}' | cut -d '.' -f1`; do\n"
	tmp += '	find . -name ""$SYSTEM"_dimer_*.sign" > "$SYSTEM".list\n'
	tmp += '	./CZ_input_zindo_mc -I $SYSTEM -i $INPUT_DIR/MD -r $DIR/results -t mc\n'
	tmp += 'done\n\n'

	tmp += 'echo "Now cleaning everything..."\n'
	tmp += 'cd $OUTPUT_DIR\n'
	tmp += "for SYSTEM in `find $INPUT_DIR/MD -maxdepth 1 -name '*.xyz' | awk -F 'input/MD/' '{print $2}' | cut -d '.' -f1`; do\n"
	tmp += '	if [[ -d $SYSTEM ]]; then\n'
	tmp += '		rm -rf $SYSTEM\n'
	tmp += '	fi\n'
	tmp += 'done\n'
	
	tmp += 'cd $RESULTS_DIR\n'
	tmp += 'rm ZINDO_sign CZ_input_zindo_mc\n'
	tmp += "for SYSTEM in `find $INPUT_DIR/MD -maxdepth 1 -name '*.xyz' | awk -F 'input/MD/' '{print $2}' | cut -d '.' -f1`; do\n"
	tmp += '	rm "$SYSTEM".list\n'
	tmp += '	mkdir -p $SYSTEM\n'
	tmp += '	for x in `find . -maxdepth 1 -name ""$SYSTEM"*.out"`; do\n'
	tmp += '		mv $x $SYSTEM\n'
	tmp += '	done\n'
	tmp += '	tar cfz "$SYSTEM"_out.tar.gz $SYSTEM\n'
	tmp += '	rm -rf $SYSTEM\n\n'

	tmp += '	mkdir -p $SYSTEM\n'
	tmp += '	for x in `find . -maxdepth 1 -name ""$SYSTEM"*.sign"`; do\n'
	tmp += '		mv $x $SYSTEM\n'
	tmp += '	done\n'
	tmp += '	tar cfz "$SYSTEM"_sign.tar.gz $SYSTEM\n'
	tmp += '	rm -rf $SYSTEM\n'
	tmp += 'done\n'
	
	
	file = 'project%s%s%s03.collect_direct.sh' % (os.sep, project.project_name, os.sep)
	try:
		foutput = open(file, 'w')
	except:
		print "[ERROR] Could not create %s. Aborting..." % (file)
		sys.exit(1)
	
	foutput.write(tmp)
	foutput.close()

# ******************************************************************************
#                Functions related to Quantum_Sampling_Generation.py
# ******************************************************************************

def CreateTINKERVisualization(X, mol, mode, tmp, filename_base, p):
	tmp += '%5d %s\n' % (mol.n_mol*mol.n_atom[0], filename_base)
	j = 0
	for i in xrange(mol.n_mol*mol.n_atom[0]):
		a = i%mol.n_mol
		b = i%mol.n_atom[i%mol.n_mol]
		tmp += '%5d %2s %12.6f %12.6f %12.6f 0\n' % (i + 1, mol.symbol[0][a][b], X[j, 0], X[j+1, 0], X[j+2, 0])
		j += 3
	
	if p:
		try:
			os.makedirs("TINKER")
		except:
			pass
		
		name = "TINKER/mode_%d.arc" % (mode+1)
		try:
			foutput = open(name, 'w')
		except:
			print "Could not open file %s" % (name)
			sys.exit(1)
		
		foutput.write(tmp)		
		foutput.close()
		
		
	return tmp

def CreateNormalMode(X, mol, mode, d):
	""" Creation of the normal modes files, like Sigi's input
	"""
	dir = "normal_modes/normal_mode_%d" % (mode+1)
	try:
		os.makedirs(dir)
	except:
		pass
	
	tmp = ''
	j = 0
	for i in xrange(mol.n_mol*mol.n_atom[0]):
		a = i%mol.n_mol
		b = i%mol.n_atom[i%mol.n_mol]
		tmp += '%2s %12.6f %12.6f %12.6f\n' % (mol.symbol[0][a][b], X[j, 0], X[j+1, 0], X[j+2, 0])
		j += 3
	
	name = "%s/result_%d_%.12f_.dat" % (dir, mode+1, d)
		
	try:
		foutput = open(name, 'w')
	except:
		print "Could not open %s" % (name)
		sys.exit(1)
		
	foutput.write(tmp)
	foutput.close()	

def CreateVBHFInput(X, mol, box, mode, d):
	""" Creation of the VBHF input files
	"""
	for charge in [-1, 0, 1]:
		try:
			dir_all="VBHF/all_%d" % (charge)
			os.makedirs(dir_all)
		except:
			pass
		try:
			dir_mono="VBHF/mono_%d" % (charge)
			os.makedirs(dir_mono)
		except:
			pass
					
		print "Calculating normal mode %d of charge %d" %(mode+1, charge)
			
		# All cluster
		name = "%s/result_%d_%.12f_.dat" % (dir_all, mode+1, d)
			
		foutput = open(name, 'w')
		
		if foutput:
			tmp = ''
			tmp = "AM1 1SCF VBHF\n\n"
			tmp += "Xx        0.0000 1     0.0000 1     0.0000 1\n"
			tmp += "Xx        0.0000 1     0.0000 1     0.0000 1\n"
			tmp += "Xx        1.0000 1     0.0000 1     0.0000 1\n"
			tmp += "Xx        0.0000 1     1.0000 1     0.0000 1\n"
			tmp += "Xx        0.0000 1     0.0000 1     1.0000 1\n" 

			k = 1
			for a in [0, -1, 1]:
				for b in [0, -1, 1]:
					j = 0
					for i in xrange(mol.n_atom[0]):
						Frac_Coord = coord_conversion.Cartesian_To_Fractional(X[j, 0], X[j+1, 0], X[j+2, 0], box)
						Frac_Coord[0] += a
						Frac_Coord[1] += b
						Cart_Coord = coord_conversion.Fractional_To_Cartesian(Frac_Coord[0], Frac_Coord[1], Frac_Coord[2], box)
						tmp += "%4s %12f 1 %12f 1 %12f 1\n" % (mol.symbol[0][0][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
						#tmp += "%5d %4s %12f %12f %12f 0\n" % (k, mol.symbol[0][1][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
						j += 3
						k += 1
					for i in xrange(mol.n_atom[1]):
						Frac_Coord = coord_conversion.Cartesian_To_Fractional(X[j, 0], X[j+1, 0], X[j+2, 0], box)
						Frac_Coord[0] += a
						Frac_Coord[1] += b
						Cart_Coord = coord_conversion.Fractional_To_Cartesian(Frac_Coord[0], Frac_Coord[1], Frac_Coord[2], box)
						tmp += "%4s %12f 1 %12f 1 %12f 1\n" % (mol.symbol[0][1][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
						#tmp += "%5d %4s %12f %12f %12f 0\n" % (k, mol.symbol[0][1][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
						j += 3
						k += 1
						
			for a in [-2, -1, 0, 1]:
				j = 0
				for i in xrange(mol.n_atom[1]):
					Frac_Coord = coord_conversion.Cartesian_To_Fractional(X[(mol.n_atom[0]*3)+j, 0], X[(mol.n_atom[0]*3)+j+1, 0], X[(mol.n_atom[0]*3)+j+2, 0], box)
					Frac_Coord[0] += a
					Frac_Coord[1] += -2
					Cart_Coord = coord_conversion.Fractional_To_Cartesian(Frac_Coord[0], Frac_Coord[1], Frac_Coord[2], box)
					tmp += "%4s %12f 1 %12f 1 %12f 1\n" % (mol.symbol[0][0][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
					#tmp += "%5d %4s %12f %12f %12f 0\n" % (k, mol.symbol[0][0][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
					j += 3
					k += 1
						
			for b in [-1, 0, 1]:
				j = 0
				for i in xrange(mol.n_atom[1]):
					Frac_Coord = coord_conversion.Cartesian_To_Fractional(X[(mol.n_atom[0]*3)+j, 0], X[(mol.n_atom[0]*3)+j+1, 0], X[(mol.n_atom[0]*3)+j+2, 0], box)
					Frac_Coord[0] += -2
					Frac_Coord[1] += b
					Cart_Coord = coord_conversion.Fractional_To_Cartesian(Frac_Coord[0], Frac_Coord[1], Frac_Coord[2], box)
					tmp += "%4s %12f 1 %12f 1 %12f 1\n" % (mol.symbol[0][0][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
					#tmp += "%5d %4s %12f %12f %12f 0\n" % (k, mol.symbol[0][0][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
					j += 3
					k += 1
		
			tmp += "$$VBHF\n"
			tmp += "%d %d AM1 OMF-OPT\n" % (mol.n_atom[0], charge)
			for x in xrange(24):
				tmp += "%d 0 AM1 OMF-OPT\n"	 % mol.n_atom[0]	

			foutput.write(tmp)		
			foutput.close() 


		# Molecule alone
		name = "%s/result_%d_%.12f_.dat" % (dir_mono, mode+1, d)
			
		foutput = open(name, 'w')
		
		if foutput:
			tmp = ''
			tmp = "AM1 1SCF VBHF\n\n"
			tmp += "Xx        0.0000 1     0.0000 1     0.0000 1\n"
			tmp += "Xx        0.0000 1     0.0000 1     0.0000 1\n"
			tmp += "Xx        1.0000 1     0.0000 1     0.0000 1\n"
			tmp += "Xx        0.0000 1     1.0000 1     0.0000 1\n"
			tmp += "Xx        0.0000 1     0.0000 1     1.0000 1\n"

			j = 0
			for i in xrange(mol.n_atom[0]):
				tmp += "%4s %12f 1 %12f 1 %12f 1\n" % (mol.symbol[0][0][i], X[j, 0], X[j+1, 0], X[j+2, 0])
				j += 3
			
			tmp += "$$VBHF\n"
			tmp += "%d %d AM1 OMF-OPT\n" % (mol.n_atom[0], charge)	

			foutput.write(tmp)		
			foutput.close()
			
def CreateMEInput(X, mol, box, mode, d):
	""" Creation of the Microelectrostatic input files
	"""

	try:
		dir_all="ME"
		os.makedirs(dir_all)
	except:
		pass
				
	print "Calculating normal mode %d" %(mode+1)
		
	# All cluster
	name = "%s/result_%d_%.12f_.dat" % (dir_all, mode+1, d)
		
	foutput = open(name, 'w')
	
	if foutput:
		tmp = ''

		ii = 1
		iii = 1
		for a in [0, -1, 1]:
			for b in [0, -1, 1]:
				j = 0
				for i in xrange(mol.n_atom[0]):
					Frac_Coord = coord_conversion.Cartesian_To_Fractional(X[j, 0], X[j+1, 0], X[j+2, 0], box)
					Frac_Coord[0] += a
					Frac_Coord[1] += b
					Cart_Coord = coord_conversion.Fractional_To_Cartesian(Frac_Coord[0], Frac_Coord[1], Frac_Coord[2], box)
					if mol.symbol[0][0][i] == "C":
						t = 2
					if mol.symbol[0][0][i] == "H":
						t = 5
					
					tmp += "%d %f %f %f %d 0 0 0 %d\n" % (iii, Cart_Coord[0], Cart_Coord[1], Cart_Coord[2], t, ii)
					#tmp += "%5d %4s %12f %12f %12f 0\n" % (k, mol.symbol[0][1][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
					j += 3
					iii += 1
				ii += 1
				
				for i in xrange(mol.n_atom[1]):
					Frac_Coord = coord_conversion.Cartesian_To_Fractional(X[j, 0], X[j+1, 0], X[j+2, 0], box)
					Frac_Coord[0] += a
					Frac_Coord[1] += b
					Cart_Coord = coord_conversion.Fractional_To_Cartesian(Frac_Coord[0], Frac_Coord[1], Frac_Coord[2], box)
					if mol.symbol[0][1][i] == "C":
						t = 2
					if mol.symbol[0][1][i] == "H":
						t = 5
					
					tmp += "%d %f %f %f %d 0 0 0 %d\n" % (iii, Cart_Coord[0], Cart_Coord[1], Cart_Coord[2], t, ii)
					#tmp += "%5d %4s %12f %12f %12f 0\n" % (k, mol.symbol[0][1][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
					j += 3
					iii += 1
				ii += 1
					
		for a in [-2, -1, 0, 1]:
			j = 0
			for i in xrange(mol.n_atom[1]):
				Frac_Coord = coord_conversion.Cartesian_To_Fractional(X[(mol.n_atom[0]*3)+j, 0], X[(mol.n_atom[0]*3)+j+1, 0], X[(mol.n_atom[0]*3)+j+2, 0], box)
				Frac_Coord[0] += a
				Frac_Coord[1] += -2
				Cart_Coord = coord_conversion.Fractional_To_Cartesian(Frac_Coord[0], Frac_Coord[1], Frac_Coord[2], box)
				if mol.symbol[0][0][i] == "C":
					t = 2
				if mol.symbol[0][0][i] == "H":
					t = 5
					
				tmp += "%d %f %f %f %d 0 0 0 %d\n" % (iii, Cart_Coord[0], Cart_Coord[1], Cart_Coord[2], t, ii)
				#tmp += "%5d %4s %12f %12f %12f 0\n" % (k, mol.symbol[0][0][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
				j += 3
				iii += 1
			ii += 1
					
		for b in [-1, 0, 1]:
			j = 0
			for i in xrange(mol.n_atom[1]):
				Frac_Coord = coord_conversion.Cartesian_To_Fractional(X[(mol.n_atom[0]*3)+j, 0], X[(mol.n_atom[0]*3)+j+1, 0], X[(mol.n_atom[0]*3)+j+2, 0], box)
				Frac_Coord[0] += -2
				Frac_Coord[1] += b
				Cart_Coord = coord_conversion.Fractional_To_Cartesian(Frac_Coord[0], Frac_Coord[1], Frac_Coord[2], box)
				if mol.symbol[0][0][i] == "C":
					t = 2
				if mol.symbol[0][0][i] == "H":
					t = 5
				
				tmp += "%d %f %f %f %d 0 0 0 %d\n" % (iii, Cart_Coord[0], Cart_Coord[1], Cart_Coord[2], t, ii)
				#tmp += "%5d %4s %12f %12f %12f 0\n" % (k, mol.symbol[0][0][i], Cart_Coord[0], Cart_Coord[1], Cart_Coord[2])
				j += 3
				iii += 1
			ii += 1

		foutput.write(tmp)		
		foutput.close() 


def ScriptVBHFLaunch(dir_cluster):
	""" Create a bash script which will create the scripts (.pbs and .run files) needed 
		to run all the VBHF calculations.
	"""
	tmp = ''
	tmp += '#!/bin/bash\n\n'
	tmp += 'DIR="%s"\n' % (dir_cluster)
	tmp += 'N_PBS=16\n\n'

	tmp += 'MakePBS(){\n'

#	if project.location_cluster == "lyra" or project.location_cluster == "adam":
	tmp += '	echo "#!/bin/bash"			>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "#$ -j y"					>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "#$ -cwd"					>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "#$ -l vf=2G"				>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "#$ -l h_cpu=600:00:00"		>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "#$ -N QS"		>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "#$ -m bea"		>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "#$ -M nicolas.g.martinelli@gmail.com"		>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo " "					>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "module load common compilers/intel/fortran/9.1 compilers/intel/cpp/9.1 libs/mkl/9.1"			>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo " "					>> $DIR/vbhf_$1.pbs\n'
	
#	else:
#		print '[ERROR] Bad cluster location. Aborting...'
#		sys.exit(1)
		
	tmp += '	echo "cd $DIR"								>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "for FILE in \`cat $DIR/vbhf_$1.dir\`"	>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "do" 									>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "	/home/nmartine/bin/vbhf \$FILE"		>> $DIR/vbhf_$1.pbs\n'
	tmp += '	echo "done" 								>> $DIR/vbhf_$1.pbs\n'
	tmp += '}\n\n'
	
	tmp += 'i=1\n'
	tmp += 'j=1\n'
	tmp += 'k=0\n\n'

	tmp += 'cd $DIR/\n\n'

	tmp += 'find . -name "*.dat" > files.tmp\n'
	tmp += 'N_DIR=`wc -l files.tmp | awk \'{print $1}\'`\n'
	tmp += 'N_STEP=$(($N_DIR/$N_PBS + 1))\n'

	tmp += 'while [ $i -le $N_PBS ]\n'
	tmp += 'do\n\n'

	tmp += '	k=$(($j+$N_STEP))\n'
	tmp += '	MakePBS $i\n'
	tmp += '	sed -n "$j","$k"p files.tmp > $DIR/vbhf_$i.dir\n\n'

	tmp += '	j=$(($k+1))\n'
	tmp += '	i=$(($i+1))\n\n'

	tmp += 'done\n\n'
	
	tmp += 'cd $DIR\n'
	tmp += 'for PBS in `ls vbhf_*.pbs`\n'
	tmp += 'do\n'
	tmp += '	qsub $PBS\n'
	tmp += 'done\n'

	file = '01.launch_vbhf.sh'
	try:
		foutput = open(file, 'w')
	except:
		print "Could not create %s. Aborting..." % (file)
		sys.exit(1)
	
	foutput.write(tmp)
	foutput.close()