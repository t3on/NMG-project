#MySQL Query of ELP data
#written by Teon Brooks 2/20/2012


print "\nEnter the input file basename: ";
chomp($base_input = <STDIN>);

	open(FILE, "$base_input.txt");
	my @input = <FILE>;
	close(FILE);
	
foreach my $trailspacetest (@input) {
	$trailspacetest =~ s/\s*$//;		# Remove trailing whitespace to avoid errors caused by 
							# $pbreak and $tbreak followed by whitespace
	}

#there's a weird apostrophe problem that is fixed here.
foreach my $apo (@input) {
	$apo =~ s/\'/\\\'/g;
	
	}
	
	
	$stimout = "${base_input}.dat";


	open (STIMOUT, ">$stimout");

#	print STIMOUT "word\t" . "word_freq\n";



#connects to the database

use DBI();
$dbh = DBI->connect('DBI:mysql:database=pling;host=neon.linguistics.fas.nyu.edu:3306', 'probe', 'query',
	            { RaiseError => 1 }
		);	

# define the query
my $sql = "SELECT * FROM elp WHERE word = ?";


# prepare the query
my $sth = $dbh->prepare($sql);
	
$i = 0;
while ($i < $#input+1)
	{
	$line = $input[$i];

# execute query
	$sth->execute($line);
	$result = $sth->fetchrow_hashref();
	push @freqs, $result->{'freq_hal'};
        
    push @nmg, $result->{'nmg'};        

#takes the escape symbol out of the word
foreach my $apo (@input) {
	$apo =~ s/\\\'/\'/g;
	
	}
$line = "'$line'";
push @words, $line;
        
	$i ++;
	}

#line entries: 1 = word, 2 = freq_hal, 3 = nmg
local $" = "\t";
print STIMOUT "\L@{words}\n" . "@{freqs}\n" . "@{nmg}\n"; 

 

close(STIMOUT);
