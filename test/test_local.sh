QDIR=_local_queue
OUTDIR=output
DIR=`dirname $0`

[[ "$1" == "" || ! -f "$1" ]] && echo "Usage: $0 TEST_JD*" && exit
rm -rf $QDIR* $OUTDIR
mkdir -p $QDIR
mkdir $OUTDIR
i=1
for f in $* ; do
  cp $f $QDIR/$i.json
  i=$[$i+1]
done

$DIR/../executors/flat/wooster.py -d $QDIR -v -n 2 -o $OUTDIR

ls -lR $OUTDIR*
