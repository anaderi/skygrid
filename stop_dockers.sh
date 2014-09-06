for p in `docker ps| tail -n +2 |awk '{print $1}' `; do 
docker stop $p & 
done 
wait
