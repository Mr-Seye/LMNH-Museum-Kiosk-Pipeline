"""A small example of a Kafka producer."""

from os import environ

from dotenv import load_dotenv
from confluent_kafka import Producer


def talk_with(producer: Producer, name: str, chat_with: str):
    message = input(f"{name}, enter your message for {chat_with}: ")

    while True:
        producer.produce(topic="cohort",
                         value=message,
                         key=chat_with)
        producer.flush()


if __name__ == "__main__":

    load_dotenv()

    kafka_producer = Producer({
        "bootstrap.servers": environ["BOOTSTRAP_SERVERS"],
        'security.protocol': environ["SECURITY_PROTOCOL"],
        'sasl.mechanisms': environ["SASL_MECHANISM"],
        'sasl.username': environ["USERNAME"],
        'sasl.password': environ["PASSWORD"]
    })

    name = input("Give your name: ")
    chat_with = input("Who do you want to chat with: ")

    talk_with(kafka_producer, name, chat_with)
