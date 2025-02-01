from openai_integration.openai_client import process_expense

if __name__ == "__main__":
    with open("receipt.jpg", "rb") as img_file:
        image_bytes = img_file.read()

    a = process_expense(text="The receipt", image_bytes=image_bytes)
    # нужно сгенерить айди чека
    # нужно добавить дату
    # нужно сохранить в бд
    print(a)
