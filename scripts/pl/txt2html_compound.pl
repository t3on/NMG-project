#txt2html.pl
#written by Teon Brooks
#October 17, 2011

print "Input filename:\nFor example \"test\" from \"test.txt\"\n: ";
$stimfile = <STDIN>;
chomp $stimfile;

open (FILE, "${stimfile}.txt");														#this opens the file. FILE is the filehandle for the file.
my @input = <FILE>;																		#this stores the content of the  file into an array to allow manipulations by perl


open(FILE, "header_compounds.txt");
my @header = <FILE>;

$stimout = "${stimfile}-1.html";													#this creates the file for the output
open(STIMOUT, ">$stimout");															#this creates the filehandle STIMOUT and it opens the file for new input
$stimout2 = "${stimfile}-2.html";													#this creates the file for the output
open(STIMOUT2, ">$stimout2");														#this creates the filehandle STIMOUT and it opens the file for new input


foreach my $quote (@input)															#this foreach loop finds any double quote and removes it 
{
	$quote =~ s/\"//g;																#this is the search and replace function. it looks for the double quote and replaces it with nothing
}

print STIMOUT "@{header}";
print STIMOUT2 "@{header}";


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
		
		print STIMOUT "<p><font size=\"4\"><b>Example ${ex_count}:</b> ${line[2]}:${line[1]} </font></p>\n";
		print STIMOUT2 "<p><font size=\"4\"><b>Example ${ex_count}:</b> ${line[2]}:${line[1]} </font></p>\n";
	
		print STIMOUT "<p> Not Related <input type=\"radio\" name=\"Example ${ex_count}\" value=\"1\" />1 <input type=\"radio\" name=\"ex${ex_count}\" value=\"2\" />2 <input type=\"radio\" name=\"ex${ex_count}\"
		value=\"3\" />3 <input type=\"radio\" name=\"ex${ex_count}\" value=\"4\" />4 <input type=\"radio\" name=\"ex${ex_count}\" value=\"5\" />5 <input type=\"radio\" name=\"ex${ex_count}\" value=\"6\" />6 
		<input type=\"radio\" name=\"ex${ex_count}\" value=\"7\" />7 Very Related</p>\n";
		print STIMOUT2 "<p> Not Related <input type=\"radio\" name=\"Example ${ex_count}\" value=\"1\" />1 <input type=\"radio\" name=\"ex${ex_count}\" value=\"2\" />2 <input type=\"radio\" name=\"ex${ex_count}\"
		value=\"3\" />3 <input type=\"radio\" name=\"ex${ex_count}\" value=\"4\" />4 <input type=\"radio\" name=\"ex${ex_count}\" value=\"5\" />5 <input type=\"radio\" name=\"ex${ex_count}\" value=\"6\" />6 
		<input type=\"radio\" name=\"ex${ex_count}\" value=\"7\" />7 Very Related</p>\n";
		
		
		print STIMOUT "<p><font size=\"4\">For this one, you might indicate <i>${line[4]}</i> or <i>${exp_value}</i> since these pairs are ${line[5]}.</font></p> <p>&nbsp\;</p> <p>&nbsp\;</p>\n";
		print STIMOUT2 "<p><font size=\"4\">For this one, you might indicate <i>${line[4]}</i> or <i>${exp_value}</i> since these pairs are ${line[5]}.</font></p> <p>&nbsp\;</p> <p>&nbsp\;</p>\n";
		
	}
}


print STIMOUT "<p>&nbsp;</p><p>&nbsp;</p><p><font size=\"4\">Now you're ready to begin the experiment!</font></p><p>&nbsp;</p>\n";
print STIMOUT2 "<p>&nbsp;</p><p>&nbsp;</p><p><font size=\"4\">Now you're ready to begin the experiment!</font></p><p>&nbsp;</p>\n";

	
for($i = $ex_count + 1; $i <= $#input; $i++)
{
	$stim_count = $i - $ex_count ;
	$stim_count = sprintf ("%03d", $stim_count);
	
	@line = split(/\t/, $input[$i]);
	chomp @line;
	$type = $line[0];
	chomp $type;
	
	$mod = $i%2;
	
if ($mod == 0)	
	{	
	print STIMOUT "<p><font size=\"4\"><b>${stim_count}: </b> ${line[2]}:${line[1]} </font></p>\n";
	print STIMOUT2 "<p><font size=\"4\"><b>${stim_count}: </b> ${line[3]}:${line[1]} </font></p>\n";
	}
else
	{	
	print STIMOUT "<p><font size=\"4\"><b>${stim_count}: </b> ${line[3]}:${line[1]} </font></p>\n";
	print STIMOUT2 "<p><font size=\"4\"><b>${stim_count}: </b> ${line[2]}:${line[1]} </font></p>\n";
	}
	
	
	print STIMOUT "<p> Not Related <input type=\"radio\" name=\"${stim_count}\" value=\"1\" />1 <input type=\"radio\" name=\"${stim_count}\" value=\"2\" />2 <input type=\"radio\" name=\"${stim_count}\"
	value=\"3\" />3 <input type=\"radio\" name=\"${stim_count}\" value=\"4\" />4 <input type=\"radio\" name=\"${stim_count}\" value=\"5\" />5 <input type=\"radio\" name=\"${stim_count}\" value=\"6\" />6 
	<input type=\"radio\" name=\"${stim_count}\" value=\"7\" />7 Very Related</p>\n";
	
	print STIMOUT2 "<p> Not Related <input type=\"radio\" name=\"${stim_count}\" value=\"1\" />1 <input type=\"radio\" name=\"${stim_count}\" value=\"2\" />2 <input type=\"radio\" name=\"${stim_count}\"
	value=\"3\" />3 <input type=\"radio\" name=\"${stim_count}\" value=\"4\" />4 <input type=\"radio\" name=\"${stim_count}\" value=\"5\" />5 <input type=\"radio\" name=\"${stim_count}\" value=\"6\" />6 
	<input type=\"radio\" name=\"${stim_count}\" value=\"7\" />7 Very Related</p>\n";

}

print STIMOUT "<p>&nbsp;</p><p>&nbsp;</p><p><font size=\"4\">Thank you for your participation.</font></p><p>&nbsp;</p>\n";
print STIMOUT2 "<p>&nbsp;</p><p>&nbsp;</p><p><font size=\"4\">Thank you for your participation.</font></p><p>&nbsp;</p>\n";



close (STIMOUT);															#this closes the file
close (STIMOUT2);

##Subroutine
sub trim
{
	$_[0] =~ s/^\s+//;
	$_[0] =~ s/\s+$//;
	return $_[0];
}