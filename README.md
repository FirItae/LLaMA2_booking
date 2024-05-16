# LLM for booking hotels/flights

## Introduction

Данный проект предназначен для запуска телеграмм бота с LLM внутри для бронирования отелей/авибилетов.
В качестве модели используется fine-tune версия LLaMA 2 с LoRA адаптером.
Обучение модели и чекпоинты хранятся в [wandb](https://wandb.ai/algolovanova/llama_for_booking_travel?nw=nwuseralgolovanova).
Лучший (последний) чекпоинт доступен на [Google диске](https://drive.google.com/drive/folders/1FpCbsxjG2sStpC3jvphyFO8fiPUx3Vhw?usp=share_link)


## Project Structure

~~~
.
├── bot_booking                  <- Telegram bot code
│   ├── logs                           <- chat history
│   ├── config.json                    <- bot configuration file
│   └── bot.py                         <- source code
├── notebooks                     <- model source code
│   ├── data_preprocessing.ipynb       <- data preproc source core 
│   └── train.py                       <- main file with training code
├── .gitignore                           
├── report.pdf                                                   
└── README.md                   
~~~

## How to Use

<details>
<summary><b>Подготовка данных и обучение</b></summary>

Весь исходный код для обучения и применения модели находится в директории [``notebooks``](./notebooks/).

</details>

<details>
<summary><b>Запуск бота</b></summary>

Для запуска бота необходимо:
 1. подгрузить веса из [wandb]((https://wandb.ai/algolovanova/llama_for_booking_travel?nw=nwuseralgolovanova)) или [Google диск](https://drive.google.com/drive/folders/1FpCbsxjG2sStpC3jvphyFO8fiPUx3Vhw?usp=share_link)

 2. создать config.json файл и положить его в папку bot_booking

```json
{
    "BOT_TOKEN":  "YOUR_BOT_TOKEN_HERE",
    "checkpoint": "PATH_TO_YOUR_CHECKPOINT_DIR_HERE",
    "logs_path":  "CHAT_HISTORY_PATH_DIR_HERE",
}
```

 3. После этого запустить [bot.py](./bot_booking/bot.py): 

```
python bot_booking/bot.py
```



</details>












