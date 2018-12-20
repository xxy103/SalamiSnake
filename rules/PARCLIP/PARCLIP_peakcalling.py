
#################
## PEAKCALLING ##
#################

# BE CAREFUL when using other protocols then you might need to define a different bitflag!!
# rule mate_reads_fitlering:
# 	input:
# 		DEDUPLICAITON_OUTDIR + "/{sample}_{replicate}_sorted.bam"
# 	output:
# 		bam=MATEFILTER_OUTDIR + "/{sample}_{replicate}.bam",
# 		sorted_bam=MATEFILTER_OUTDIR + "/{sample}_{replicate}_sorted.bam",
# 		sorted_bam_bai=MATEFILTER_OUTDIR + "/{sample}_{replicate}_sorted.bam.bai"
# 	threads: 2
# 	conda:
# 		config["conda_envs"] + "/samtools.yml"
# 	shell:
# 		"if [ ! -d {MATEFILTER_OUTDIR} ]; then mkdir {MATEFILTER_OUTDIR}; fi"
# 		"&& samtools view -b -F 0x100 {input} > {output.bam}"
# 		"&& samtools sort {output.bam} > {output.sorted_bam}"
# 		"&& samtools index {output.sorted_bam}"

# rule piranha:
# 	input:
# 		MATEFILTER_OUTDIR + "/{sample}_{replicate}_sorted.bam"
# 	output:
# 		PEAKCALLING_OUTDIR + "/{sample}_{replicate}_peaks.bed"
# 	conda:
# 		config["conda_envs"] + "/piranha.yml"
# 	threads: 2 
# 	shell:
# 		"if [ ! -d {PEAKCALLING_OUTDIR} ]; then mkdir {PEAKCALLING_OUTDIR}; fi"
#		"&& echo {config[prianha]} >> {file_tool_params}"
# 		"&& Piranha {config[prianha]} {input} -o {output}"

rule pureclip:
	input:
		experiment=PRE_FOR_UMI_OUTDIR + "/{sample}_{replicate}_got_umis_unlocalized_check.bam",
		experiment_bai=PRE_FOR_UMI_OUTDIR + "/{sample}_{replicate}_got_umis_unlocalized_check.bam.bai",
		genome_fasta=GENOME_FASTA
	output:
		crosslinking_sites=PEAKCALLING_OUTDIR + "/{sample}_{replicate}_crosslinkind_sites.bed",
		binding_regions=PEAKCALLING_OUTDIR + "/{sample}_{replicate}_binding_regions.bed"
	threads: 4
	params:
		tmp=PEAKCALLING_OUTDIR + "/tmp/",
		parameters=PEAKCALLING_OUTDIR + "/{sample}_{replicate}_parameters.txt"
	conda:
		config["conda_envs"] + "/pureclip.yml"
	shell:
		"if [ ! -d {PEAKCALLING_OUTDIR} ]; then mkdir {PEAKCALLING_OUTDIR}; fi "
		"&& echo {config[pureclip]} >> {file_tool_params}"
		"&& pureclip -i {input.experiment} -bai {input.experiment_bai} -g {input.genome_fasta} -o {output.crosslinking_sites} -tmp {params.tmp} "
		"-or {output.binding_regions} -p {params.parameters} -nt {threads} -nta {threads} {config[pureclip]} "

rule peaks_extend_frontiers:
	input:
		bed=PEAKCALLING_OUTDIR + "/{sample}_{replicate}_binding_regions.bed",
		genome=GENOME_SIZES
	output:
		PEAKCALLING_OUTDIR + "/{sample}_{replicate}_peaks_extended.bed"
	threads: 2
	conda:
		config["conda_envs"] + "/bedtools.yml"
	shell:
		"echo {config[peaks_extend_frontiers]} >> {file_tool_params}"
		"&& bedtools slop {config[peaks_extend_frontiers]} -i {input.bed} -g {input.genome} > {output}"

rule find_robust_peaks:
	input:
		expand(PEAKCALLING_OUTDIR + "/{sample}_{replicate}_peaks_extended.bed", sample=SAMPLES[0], replicate=REP_NAME_CLIP)
	output:
		ROBUSTPEAKS_OUTDIR + "/robust_between_all.bed"
	threads: 2
	conda:
		config["conda_envs"] + "/bedtools.yml"
	params:
		input_folder=PEAKCALLING_OUTDIR,
		output_folder=ROBUSTPEAKS_OUTDIR
	shell:
		"if [ ! -d {ROBUSTPEAKS_OUTDIR} ]; then mkdir {ROBUSTPEAKS_OUTDIR}; fi"
		"&& {config[find_robust_intersections]}/robust_intersections.sh {params.input_folder} {params.output_folder} bed"