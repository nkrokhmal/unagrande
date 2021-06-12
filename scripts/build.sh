sh save_last_batches.sh &&
cd .. &&
git checkout db/prod/  &&
git pull &&
python3 tests/runners/runners/run_tests.py &&
docker-compose down &&
docker-compose up --build -d &&
cd scripts &&
sleep 7 &&
sh upload_last_batches.sh