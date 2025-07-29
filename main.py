import logging
import time
import util
from bot import Bot


def main():
    logging.basicConfig(format="%(levelname)s: %(asctime)s - %(message)s",
                        datefmt="%I:%M:%S", level=logging.INFO)
    logging.info("Starting bot")

    settings = util.get_settings()
    ticket = settings['ticket']
    notification = settings['notification']
    logging.info("Retrieved data from json file")

    bot = Bot(ticket["magicLink"].strip())
    logging.info("Initialized a bot instance")

    time.sleep(2)
    logging.info("Navigating to start page")
    bot.go_to_start_page()

    time.sleep(2)
    logging.info("Navigating to festival page")
    bot.go_to_festival_page(ticket['festivalName'].strip())

    time.sleep(2)
    logging.info("Navigating to ticket page")
    bot.go_to_ticket_page(ticket["otherCategory"].strip(), ticket["ticketName"].strip())

    time.sleep(2)
    logging.info("Starting to look for available tickets")
    while bot.find_available() is False:
        logging.warning("No tickets found, trying again...")
        bot.refresher()

    logging.info("Ticket(s) found!")
    
    # Check price if max_price is set
    max_price = ticket.get("maxPrice")
    if max_price and not bot.check_price(max_price):
        logging.warning("Ticket price exceeds budget, continuing to search...")
        bot.refresher()
        return main()  # Restart the search

    logging.info("Reserving ticket")
    bot.reserve_ticket()

    logging.info("Dialing user")
    bot.dial_number(notification["twilioPhone"], notification["phone"], notification["sid"], notification["token"])

    logging.info("Waiting for checkout completion")
    time.sleep(900) # 15 minutes of buffer time to complete checkout

    logging.info("Closing bot")
    bot.quit()


if __name__ == "__main__":
    main()
