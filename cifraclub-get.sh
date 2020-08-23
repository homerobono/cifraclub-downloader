#!/bin/bash

base_url='https://www.cifraclub.com.br'
params='imprimir.html#tabs=false&columns=true'
artists=(`[ -n $1 ] && cat $1 || echo artists.txt`)

function get_artistsongs {
    artist=$1
    artist_name=`echo $artist | sed -e 's/-/ /g' -e 's/\(^\| \)\(.\)/\1\u\2/g'`
    index_file=cifras/$artist/songs_index.dat
    tmp_index_file=cifras/$artist/.songs_index.tmp.dat
    diff_file=cifras/$artist/.index.diff
    
    python3 get_songs_from_html.py $base_url $artist > $tmp_index_file
    
    if [ -f $index_file ]
    then
	diff <(sort $index_file) <(sort $tmp_index_file) > $diff_file
	new=(`grep '>' $diff_file | sed -e 's/> *//'`)
	absent=(`grep '<' $diff_file | sed -e 's/< *//'`)
	echo $new >> $index_file
	rm $diff_file $tmp_index_file
    else
	mv $tmp_index_file $index_file
        new=(`cat $index_file`)
    fi

    if [ $new ]
    then
        echo Found ${#new[*]} new ciphers for $artist_name:
        for cipher in ${new[*]}; do echo $cipher; done
    else
	echo No new ciphers for $artist_name
    fi

    if [ $absent ]
    then
        echo Couldn\'t find ${#absent[*]} ciphers for $artist_name:
        for cipher in ${absent[*]}; do echo $cipher; done
    fi

    url="$base_url/$artist/#instrument=guitar"
}

function assemble_url {
    song=`echo $1 | sed -e "s/\.html//g"`
    url="$base_url/$song/$params"
    echo $url
}

mkdir -p cifras css img
	
for artist in ${artists[@]}; do
  (
    mkdir -p cifras/$artist
    get_artistsongs $artist
    index_file=cifras/$artist/songs_index.dat
    songs=(`cat $index_file`)

    if [[ ${#songs[*]} -eq 0 ]]; then
        echo "No songs found for $artist"
	rmdir cifras/$artist
	continue
    fi
    
    # echo Found ${#songs[*]} ciphers for $artist

    for version in ${songs[*]}; do
      (
	if echo $version | egrep -q '\.html$'
	then
	    version_path=$version
	else
	    version_path=$version/principal.html
	fi

	version_path="cifras/$version_path"
	
	if [ -f cifras/$version_path ]; then
	    #echo "skipping $cifra"
	    continue
        fi

        url=$(assemble_url $version)

	mkdir -p `dirname $version_path`
	curl -s $url -o $version_path 
	
	python3 html_cleaner.py $version_path
	sed -i -e 's/tam_a4//g' $version_path
      ) &
      s_pids+=($!)
    done
   for pid in ${s_pids[*]}; do wait $pid; done
  ) &
  pids+=($!)
done

for pid in ${pids[*]}; do wait $pid; done
echo Done
