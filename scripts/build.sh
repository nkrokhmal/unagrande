cd .. && cd scripts && sh save_last_batches.sh && cd .. && git checkout db/prod/  && git pull && docker-compose up --build -d && cd scripts && sleep 7 && sh upload_last_batches.sh
