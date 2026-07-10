import asyncio

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs the Telegram bot (aiogram 3, long polling)."

    def handle(self, *args, **options):
        # Deferred import: by the time this command runs, Django is already
        # fully set up (manage.py calls django.setup() for us), so it's safe
        # to import modules that touch models/settings here.
        from bot.main import run_polling

        self.stdout.write(self.style.SUCCESS("Bot ishga tushmoqda... (Ctrl+C bilan to'xtatish)"))
        try:
            asyncio.run(run_polling())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Bot to'xtatildi."))