
int main(int argc, char* argv[])
{
	if( argc <= 1 ) {
		fprintf(stderr,"Usage: %s filename\n",argv[0]);
		return 0;
	}

	char *filename = argv[1];
	FILE *fp;
	if( ( fp = fopen( filename, "rb" ) ) == NULL ) {
		fprintf(stderr,"%s not found\n",argv[1]);
		return 0;
	}

	fprintf(stdout,"Filename = %s\n",filename);
	fprintf(stdout,"\n");

	/********** Basic Information **********/
	// Get offset of basic information
	fseek( fp, 16, SEEK_SET );
	long int basic_offset;
	fread( &basic_offset, sizeof(long int), 1, fp );

	// Read basic information
	fseek( fp, basic_offset, SEEK_SET );
	int version,revision,system_id;
	char system_name[128],model_name[128];
	int channel_count;
	char comment[256];
	fread( &version, sizeof(int), 1, fp );
	fread( &revision, sizeof(int), 1, fp );
	fread( &system_id, sizeof(int), 1, fp );
	fread( &system_name, sizeof(char), 128, fp );
	fread( &model_name, sizeof(char), 128, fp );
	fread( &channel_count, sizeof(int), 1, fp );
	fread( &comment, sizeof(char), 256, fp );

	// Output basic information
	fprintf(stdout,"Basic information\n");
	fprintf(stdout,"\tMeg160 version = V%dR%03d\n",version,revision);
	fprintf(stdout,"\tSystem ID      = %d\n",system_id);
	fprintf(stdout,"\tSystem name    = %s\n",system_name);
	fprintf(stdout,"\tModel name     = %s\n",model_name);
	fprintf(stdout,"\tChannel count  = %d\n",channel_count);
	fprintf(stdout,"\tComment        = %s\n",comment);
	fprintf(stdout,"\n");


	/********** Sensitivity Values **********/
	// Get offset of sensitivity values
	fseek( fp, 80, SEEK_SET );
	long int sensitivity_offset;
	fread( &sensitivity_offset, sizeof(long int), 1, fp );

	// Read sensitivity data
	fseek( fp, sensitivity_offset, SEEK_SET );
	double sensitivity[256*2];
	fread( &sensitivity, sizeof(double)*2, channel_count, fp );

	// Output basic information
	fprintf(stdout,"Sensitivity data\n");
	for( int k=0; k<channel_count; k++ ) {
		fprintf(stdout,"\tChannel %3d: offset = %.3lf[Volt], gain=%13.5le[Tesla/Volt]\n",k,sensitivity[k*2],sensitivity[k*2+1]);
	}
	fprintf(stdout,"\n");

	
	/********** Amplifier Information **********/
	// Get offset of amplifier information
	fseek( fp, 112, SEEK_SET );
	long int amp_offset;
	fread( &amp_offset, sizeof(long int), 1, fp );

	// Read amplifier data
	fseek( fp, amp_offset, SEEK_SET );
	int amp_data;
	fread( &amp_data, sizeof(int), 1, fp );

	// Output amplifier data
	fprintf(stdout,"Amplifier information\n");

	// Input gain is stored in Bit-11 to 12
	//  0:x1, 1:x2, 2:x5, 3:x10
#define InputGainBit			(11)
#define InputGainMask			(0x1800)
	int input_gain = ( amp_data & InputGainMask ) >> InputGainBit;
	if( input_gain == 0 )			fprintf(stdout,"\tInput gain  = x1\n");
	else if( input_gain == 1 )		fprintf(stdout,"\tInput gain  = x2\n");
	else if( input_gain == 2 )		fprintf(stdout,"\tInput gain  = x5\n");
	else if( input_gain == 3 )		fprintf(stdout,"\tInput gain  = x10\n");

	// Output gain is stored in Bit-0 to 2
	//  0:x1, 1:x2, 2:x5, 3:x10, 4:x20, 5:x50, 6:x100, 7:x200
#define OutputGainBit			(0)
#define OutputGainMask			(0x0007)
	int output_gain = ( amp_data & OutputGainMask ) >> OutputGainBit;
	if( output_gain == 0 )			fprintf(stdout,"\tOutput gain = x1\n");
	else if( output_gain == 1 )		fprintf(stdout,"\tOutput gain = x2\n");
	else if( output_gain == 2 )		fprintf(stdout,"\tOutput gain = x5\n");
	else if( output_gain == 3 )		fprintf(stdout,"\tOutput gain = x10\n");
	else if( output_gain == 4 )		fprintf(stdout,"\tOutput gain = x20\n");
	else if( output_gain == 5 )		fprintf(stdout,"\tOutput gain = x50\n");
	else if( output_gain == 6 )		fprintf(stdout,"\tOutput gain = x100\n");
	else if( output_gain == 7 )		fprintf(stdout,"\tOutput gain = x200\n");

	fprintf(stdout,"\n");


	/********** Acquisition Parameters **********/
	// Get offset of acquisition parameters
	fseek( fp, 128, SEEK_SET );
	long int acqcond_offset;
	fread( &acqcond_offset, sizeof(long int), 1, fp );

	fprintf(stdout,"Acquisition parameters\n");

	// Read acquisition type
	fseek( fp, acqcond_offset, SEEK_SET );
	long int acq_type;
	fread( &acq_type, sizeof(long int), 1, fp );

	if( acq_type == 1 ) {
		double sample_rate;
		long int sample_count,actual_sample_count;
		// Read acquisition parameters
		fread( &sample_rate, sizeof(double), 1, fp );
		fread( &sample_count, sizeof(long int), 1, fp );
		fread( &actual_sample_count, sizeof(long int), 1, fp );
		long int raw_offset;
		fseek( fp, 144, SEEK_SET );
		fread( &raw_offset, sizeof(long int), 1, fp );
		// Output acquisition parameters
		fprintf(stdout,"\tContinuous mode, Raw data file\n");
		fprintf(stdout,"\tSampling Rate       = %lg[Hz]\n",sample_rate);
		fprintf(stdout,"\tSample Count        = %ld[sample]\n",sample_count);
		fprintf(stdout,"\tActual Sample Count = %ld[sample]\n",actual_sample_count);
		fprintf(stdout,"\tData Offset         = %ld[byte]\n",raw_offset);
	}
	else if( acq_type == 2 ) {
		double sample_rate;
		long int frame_length,pretrigger_length,average_count,actual_average_count;
		// Read acquisition parameters
		fread( &sample_rate, sizeof(double), 1, fp );
		fread( &frame_length, sizeof(long int), 1, fp );
		fread( &pretrigger_length, sizeof(long int), 1, fp );
		fread( &average_count, sizeof(long int), 1, fp );
		fread( &actual_average_count, sizeof(long int), 1, fp );
		// Output acquisition parameters
		fprintf(stdout,"\tEvoked mode, Average data file\n");
		fprintf(stdout,"\tSampling Rate        = %lg[Hz]\n",sample_rate);
		fprintf(stdout,"\tFrame Length         = %ld[sample]\n",frame_length);
		fprintf(stdout,"\tPretrigger Length    = %ld[sample]\n",pretrigger_length);
		fprintf(stdout,"\tAverage Count        = %ld\n",average_count);
		fprintf(stdout,"\tActual Average Count = %ld\n",actual_average_count);
	}
	else if( acq_type == 3 ) {
		double sample_rate;
		long int frame_length,pretrigger_length,average_count,actual_average_count;
		// Read acquisition parameters
		fread( &sample_rate, sizeof(double), 1, fp );
		fread( &frame_length, sizeof(long int), 1, fp );
		fread( &pretrigger_length, sizeof(long int), 1, fp );
		fread( &average_count, sizeof(long int), 1, fp );
		fread( &actual_average_count, sizeof(long int), 1, fp );
		// Output acquisition parameters
		fprintf(stdout,"\tEvoked mode, Raw data file\n");
		fprintf(stdout,"\tSampling Rate        = %lg[Hz]\n",sample_rate);
		fprintf(stdout,"\tFrame Length         = %ld[sample]\n",frame_length);
		fprintf(stdout,"\tPretrigger Length    = %ld[sample]\n",pretrigger_length);
		fprintf(stdout,"\tAverage Count        = %ld\n",average_count);
		fprintf(stdout,"\tActual Average Count = %ld\n",actual_average_count);
	}
	else {
		printf("Quack !\n");
	}

	fprintf(stdout,"\n");

	/********** Data Block **********/
	fprintf(stdout,"Data block\n");
	// Read offset according to data type
	if( acq_type == 1 ) {
		long int raw_offset;
		fseek( fp, 144, SEEK_SET );
		fread( &raw_offset, sizeof(long int), 1, fp );
		fprintf(stdout,"\tData Type                  = 2-byte Integer\n");
		fprintf(stdout,"\tData Offset from File Head = %ld[byte]\n",raw_offset);
	}
	else if( acq_type == 2 ) {
		long int ave_offset;
		fseek( fp, 160, SEEK_SET );
		fread( &ave_offset, sizeof(long int), 1, fp );
		fprintf(stdout,"\tData Type                  = 8-byte Real\n");
		fprintf(stdout,"\tData Offset from File Head = %ld[byte]\n",ave_offset);
	}
	else if( acq_type == 3 ) {
		long int raw_offset;
		fseek( fp, 144, SEEK_SET );
		fread( &raw_offset, sizeof(long int), 1, fp );
		fprintf(stdout,"\tData Type                  = 2-byte Integer\n");
		fprintf(stdout,"\tData Offset from File Head = %ld[byte]\n",raw_offset);
	}
	else {
		printf("Oops !\n");
	}

	fclose(fp);

	return 0;
}
