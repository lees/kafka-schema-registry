# kafka-schema-registry
Здесь будет рассмотрен пример заворачивания Schema Registry поверх managed  Apache Kafka кластера в Yandex Cloud.

### Создание кластера
- Создаем тестовый кластер
```bash
yc kafka cluster create --name test --network-name <network> --zone-ids ru-central1-b --brokers-count 1 --resource-preset s2.micro --disk-size 30 --disk-type network-ssd 
```
- Сразу создаем топик для данных
```bash
yc kafka topic create --cluster-name test --replication-factor 1 --partitions 3 topic
```
- И пользователя для подключения
```bash
yc kafka user create --cluster-name test --password UserPassword \
--permission topic=topic,role=ACCESS_ROLE_CONSUMER,role=ACCESS_ROLE_PRODUCER \
user
```
- Сразу создаем топик для схем
```bash
yc kafka topic create --cluster-name test --replication-factor 1 --partitions 1 _schemas
```
- И пользователя для подключения
```bash
yc kafka user create --cluster-name test --password RegistryPassword \
--permission topic=_schemas,role=ACCESS_ROLE_CONSUMER,role=ACCESS_ROLE_PRODUCER \
registry
```

### Настройка Schema-Registry
- Создаем виртуальную машину Compute на базе Ubuntu
  - В той же сети
  - С публичным IP адресом
  - С указанным ssh ключом для подключения
- Когда машина создастся, смотрим какой у нее публичный IP и подключаемся к ней по ssh
- Устанавливаем jre
```bash
sudo apt install openjdk-11-jre-headless
```
- Следуя инструкции для подключения к кластеру для Java, создаем хранилище для сертификата
```bash
mkdir -p /usr/local/share/ca-certificates/Yandex
wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" -O /usr/local/share/ca-certificates/Yandex/YandexCA.crt
keytool -keystore client.truststore.jks -alias CARoot -import -file /usr/local/share/ca-certificates/Yandex/YandexCA.crt
cp client.truststore.jks /etc/schema-registry/
```
- Заполняем настройки пользователя для подключения к кластеру
```bash
cat << EOF > /etc/schema-registry/jaas.conf
KafkaClient {
    org.apache.kafka.common.security.scram.ScramLoginModule required
    username="user"
    password="UserPassword";
};
EOF
```
- И прописываем этот файл в параметры сервиса schema registry. Для этого нужно добавить строчку в /lib/systemd/system/confluent-schema-registry.service
```
Environment="_JAVA_OPTIONS='-Djava.security.auth.login.config=/etc/schema-registry/jaas.conf'"
```
- И после этого обновить systemd
```bash
systemctl daemon-reload
```
- Нам осталось добавить настройки в конфиг schema registry - /etc/schema-registry/schema-registry.properties
```
kafkastore.bootstrap.servers=SASL_SSL://<broker_fqdn>:9091
kafkastore.ssl.truststore.location=/etc/schema-registry/client.truststore.jks
kafkastore.ssl.truststore.password=339073
kafkastore.sasl.mechanism=SCRAM-SHA-512
kafkastore.security.protocol=SASL_SSL
```
- И запустить сервис
```bash
systemctl start confluent-schema-registry.service
```

### Проверка работы
- Установка пакета
```bash
apt install python3-pip
pip install confluent-kafka
```
- Запускаем producer
```bash
python3 producer.py
```
- Проверяем что сообщение успешно записалось
```bash
python3 consumer.py
```