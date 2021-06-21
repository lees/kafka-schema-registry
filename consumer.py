from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


c = AvroConsumer({
    'bootstrap.servers': 'rc1c-aaaaaaaaaaa.mdb.yandexcloud.net:9091',
    'group.id': 'avro-consumer',
    'security.protocol': 'SASL_SSL',
    'ssl.ca.location': '/usr/local/share/ca-certificates/Yandex/YandexCA.crt',
    'sasl.mechanism': 'SCRAM-SHA-512',
    'sasl.username': 'user',
    'sasl.password': 'UserPassword',
    'schema.registry.url': 'http://localhost:8081'})

c.subscribe(['topic'])

while True:
    try:
        msg = c.poll(10)

    except SerializerError as e:
        print("Message deserialization failed for {}: {}".format(msg, e))
        break

    if msg is None:
        continue

    if msg.error():
        print("AvroConsumer error: {}".format(msg.error()))
        continue

    print(msg.value())

c.close()