"""
please fully read docs of https://github.com/meilisearch/meilisearch-python

then make a cli using typer in this file

I want commands to
create-index (pass name of index)
command to populate the index with files in folder
command is add-to-index
--directory [str] and --extensions .py,.ps1,.sh

command to rebuild index

coimmand to search
command show stats and rop index

learn from my style of building apps like this #file:msearch.py 

and add option when building index to say --symantic (means use ai locall embedding to build the index)

in all cases we should be able to pass
MEILI_URL="http://localhost:7700" (default)
MEILI_MASTER_KEY="YOUR_MASTER_KEY"

"""