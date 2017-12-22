#!/usr/bin/perl --
#Dariusz Skiciak

use strict;
use LWP;
use HTTP::Request::Common;
use HTML::TreeBuilder;
use Getopt::Long;
use Term::ANSIColor;
use feature qw(say switch);
use Getopt::Long qw(GetOptions);

my $urlUsers    = '';
my $counterLine = 0;
my $bytes       = 0;
my $help        = '';
my $file        = '';
my $urlOpt      = '';
my $filename    = '';
my $fh;

GetOptions( 'help' => \$help, 'file' => \$file, 'url' => \$urlOpt );

if ($file) {
    say();
    print('PODAJ NAZWE PLIKU DO ZAPISU: ');

    $filename = <STDIN>;
    chomp($filename);
    if ( $filename =~ /((\.[^.\s]+)+)$/ ) {
        open( $fh, '>', $filename ) or die "Could not open file '$filename' !";
    }
    else {
        say color('bold red');
        say();
        say(' ------------------------ ERROR ----------------------- ');
        say(' |                                                    |');
        say(' |       Podana nazwa pliku jest nie poprawna!        |');
        say(' |                                                    |');
        say(' ------------- SKRYPT ZAKONCZYL DZIALNIE! ------------- ');
        say();
        say color('reset');
        exit 1;
    }
}

if ($help) {
    say();
    say('OPIS DZIALANIA PROGRAMU: ');
    say();
    say(
' Skrypt ma zadanie z parsowac plik html. Domyślnie porogram poprosci od podanie url do html, ktory chcemy sparsowac np. http://www.google.pl'
    );
    say(' Opcje: ');
    say('   -> -h | --help : wypisuje help z opisem dzialania pragramu');
    say('   -> -f | --file : zapisuje wynik prasowania do pliku');

    #    say ('   -> -u : url do html, ktorego chcemy sparcowac');
    say();
    exit 0;
}

print('PODAJ URL DO PARSOWANIA: ');
$urlUsers = <STDIN>;
chomp($urlUsers);
if ( $urlUsers =~ /^https?\:\/\/[^\s]+[\/\w]+$/ ) {
    generateTree($urlUsers);
    summary();
}
else {
    say color('bold red');
    say();
    say(' ------------------------ ERROR ----------------------- ');
    say(' |                                                    |');
    say(' |            Podany URL jest nie poprawny!           |');
    say(' |                                                    |');
    say(' ------------- SKRYPT ZAKONCZYL DZIALNIE! ------------- ');
    say();
    say color('reset');
    exit 1;
}

sub generateTree {
    my $url      = shift @_;
    my $HTMLTree = HTML::TreeBuilder->new();

    my $ua = LWP::UserAgent->new( agent => "parsepage/1.0 libwww-perl" );
    my $req = HTTP::Request->new( GET => $url );

    sub dataOfReq {
        my ( $data, $response ) = @_;
        if ( $response->content_type() eq 'text/html' ) {
            $HTMLTree->parse($data);
        }
        else {
            $HTMLTree->eof;
        }
    }
    my $resp = $ua->request( $req, \&dataOfReq );

    if ( $resp->is_success ) {
        if ( $resp->content_type() ne 'text/html' ) {
            $resp->code(410);
            $resp->message("Not HMTL");
            say color('bold red');
            say();
            say(' ------------------------ ERROR ----------------------- ');
            say(' |                                                    |');
            say(' |         URL nie prowadzi do zawartosci html        |');
            say(' |                                                    |');
            say(' ------------- SKRYPT ZAKONCZYL DZIALNIE! ------------- ');
            say();
            say color('reset');
            exit 1;
        }
        $HTMLTree->eof;
        $HTMLTree->elementify();

        printTree( 0, $HTMLTree );
    }
    else {
        say color('bold red');
        say();
        say(' ------------------------ ERROR ----------------------- ');
        say(' |                                                    |');
        say(' |             URL nie mozna polaczyc sie!            |');
        say(' |                                                    |');
        say(' ------------- SKRYPT ZAKONCZYL DZIALNIE! ------------- ');
        say();
        say color('reset');
        exit 1;
    }
}

sub printString {
    my $depth     = shift @_;
    my $string    = shift @_;
    my $oldSpaces = ' ' x $depth;
    my $newSpaces = ' ' x ( $depth + 4 );
    my $spaces    = $oldSpaces;

    return if ( $string =~ /^\s*$/m );

    $string =~ s/^\s+//;
    $string =~ s/\n\s*/\n$newSpaces/g;

    if ($file) {
        $counterLine += 1;
        print $counterLine, '. ';
        $bytes += length( $counterLine + '. ' );

        print "$spaces$string\n";
        print $fh "$spaces$string\n";
        $bytes += length( $spaces + $string + '\n' );
    }
    else {
        $counterLine += 1;
        print $counterLine, '. ';
        $bytes += length( $counterLine + '. ' );

        print "$spaces$string\n";
        $bytes += length( $spaces + $string + '\n' );
    }
}

# Print the tree HTML
sub printTree {
    my $depth = shift @_;
    my $node  = shift @_;

    if ( ref $node ) {
        printString( $depth, $node->starttag() );
    }
    else {
        printString( $depth, HTML::Entities::encode($node) );
    }

    if ( ref $node ) {
        foreach my $child ( $node->content_list() ) {
            printTree( $depth + 4, $child )
              ;    # $depth + 4 wciecie zagnieżdzonych zacznikow html
        }
        if ( !$HTML::Tagset::emptyElement{ $node->tag() } ) {
            if ($file) {
                use bytes;
                $counterLine += 1;
                print $counterLine, '. ';
                $bytes += length( $counterLine + '. ' );

                print ' ' x $depth;
                my $tmp = ' ' x $depth;
                print $fh $tmp;
                $bytes += length( ' ' x $depth );

                print '</', $node->tag(), ">\n";
                $bytes += length( '</' + $node->tag() + ">\n" );

                print $fh '</', $node->tag(), ">\n";
            }
            else {
                use bytes;
                $counterLine += 1;
                $bytes += length( $counterLine + '. ' );
                print $counterLine, '. ';

                print( ' ' x $depth );
                $bytes += length( ' ' x $depth );

                print '</', $node->tag(), ">\n";
                $bytes += length( '</' + $node->tag() + ">\n" );
            }
        }
    }
}

sub summary {
    say();
    print color('bold yellow');
    say('----------------- SUMMARY --------------------');
    print color('reset');
    say();
    say( ' URL: ', $urlUsers );
    say();
    say( ' Przenalizowano: ', $counterLine, ' lini.' );
    say( ' Bytes: ', $bytes );

    if ($file) {
        say( ' Wyniki zapisano w: ', $filename );
    }

    say();
    print color('bold yellow');
    say('--------------- END SUMMARY -----------------');
    print color('reset');
    say();
}

if ($file) {
    close $fh;
}
