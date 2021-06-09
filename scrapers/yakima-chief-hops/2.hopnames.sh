#!/bin/zsh
#Script seems to need zsh for odd characters.

#Grep for page break ASCII char then use sed to clean up.
# ^\f is page break, we also remove restricted, trademark,
# replace duplicate whitespaces with a single,
# remove ' BRAND', remove empty lines (^$/d),
# and remove trailing space (\s*$).

grep $'^\f' pdf.txt |
    sed -e 's/^\f//g;
            s/®//g;
            s/™//g;
            s/\s\{2,\}/ /g;
            s/ BRAND//g;
            /^$/d;
            s/\s*$//g' > hopnames.txt

