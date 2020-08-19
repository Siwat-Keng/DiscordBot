class Notification:

    def __init__(self, message, role, weekday=None, day=None, month=None, 
    year=None, hour=None, minute=None, second=None):
        self.state = True
        self.weekday = weekday
        self.day = day
        self.month = month
        self.year = year
        self.hour = hour
        self.minute = minute
        self.second = second
        self.message = message
        self.role = role

    def get_weekday(self, time):
        if not self.weekday:
            return True
        return time.weekday() == self.weekday

    def get_day(self, time):
        if not self.day:
            return True
        return time.day == self.day        

    def get_month(self, time):
        if not self.month:
            return True
        return time.month == self.month

    def get_year(self, time):
        if not self.year:
            return True
        return time.year == self.year

    def get_hour(self, time):
        if not self.hour:
            return True
        return time.hour == self.hour

    def get_minute(self, time):
        if not self.minute:
            return True
        return time.minute == self.minute

    def get_second(self, time):
        if not self.second:
            return True
        return time.second == self.second                                

    def notify(self, time):
        if self.get_weekday(time) and self.get_day(time) and self.get_month(time) and self.get_year(time) and \
            self.get_hour(time) and self.get_minute(time) and self.get_second(time) and not self.state:
            self.state = True
            return True
        elif not (self.get_weekday(time) and self.get_day(time) and self.get_month(time) and self.get_year(time) and \
            self.get_hour(time) and self.get_minute(time) and self.get_second(time)):
            self.state = False
            return False
        else:
            return False

    def get_message(self):
        return ' '.join([self.message, self.role.mention])