QDIR=_local_queue
OUTDIR=output
DIR=`dirname $0`

[[ "$1" == "" || ! -f "$1" ]] && echo "Usage: $0 TEST_JD" && exit
INPUT=$1
rm -rf $QDIR* $OUTDIR
mkdir -p $QDIR
mkdir $OUTDIR
cp $INPUT $QDIR/1.json

$DIR/../executors/flat/wooster.py -d $QDIR -v -n 2 -o $OUTDIR

ls -lR $OUTDIR*
