#txt2html.pl
#written by Teon Brooks
#October 17, 2011

print "Input filename:\nFor example \"test\" from \"test.txt\"\n: ";
$stimfile = <STDIN>;
chomp $stimfile;

open (FILE, "${stimfile}.txt");														#this opens the file. FILE is the filehandle for the file.
my @input = <FILE>;																		#this stores the content of the  file into an array to allow manipulations by perl


$stimout3 = "constituent-1.txt";													#this creates the file for the output
open(STIMOUT3, ">$stimout3");
$stimout4 = "constituent-2.txt";													#this creates the file for the output
open(STIMOUT4, ">$stimout4");
$stimout5 = "compound.txt";															#this creates the file for the output
open(STIMOUT5, ">$stimout5");

foreach my $quote (@input)															#this foreach loop finds any double quote and removes it 
{
	$quote =~ s/\"//g;																#this is the search and replace function. it looks for the double quote and replaces it with nothing
}

print STIMOUT3 "c1_string = [";
print STIMOUT4 "c2_string = [";
print STIMOUT5 "compound_string = [";


$i = 1;																				#this is one to ignore the header line of the list
for($i; $i <= $#input; $i++)
{
	@line = split(/\t/, $input[$i]);
	$type = $line[0];
	chomp $type;

	if ($type eq "ex")
	{

		##This is for the example block
		#line[0] = type
		#line[1] = compound
		#line[2] = first constituent
		#line[3] = second constituent
		#line[4] = exp value
		#line[5] = description

		$exp_stim = $line[1];
		$ex_count = $i;
		$exp_value = $line[4] + 1;

	}
}


	
for($i = $ex_count + 1; $i <= $#input; $i++)
{
	$stim_count = $i - $ex_count ;
	$stim_count = sprintf ("%03d", $stim_count);
	
	@line = split(/\t/, $input[$i]);
	chomp @line;
	$type = $line[0];
	chomp $type;
	
	print STIMOUT3 "{'$line[2]'}\t";
	print STIMOUT4 "{'$line[3]'}\t";
	print STIMOUT5 "{'$line[1]'}\t";

}

print STIMOUT3 "];";
print STIMOUT4 "];";
print STIMOUT5 "];";
