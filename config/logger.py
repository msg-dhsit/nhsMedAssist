import logging

def logit(logPath, fileName):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("{0}/{1}.log".format(logPath,fileName)),
            logging.StreamHandler()
        ]
    )
    return logging