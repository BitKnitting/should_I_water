# ######################################################################
# makePNG creates an image of the moisture level read by the moisture
# sensors in the front yard.
# There are three planters (p1,p2,p3)
# Each planter has 5 water sensors...hopefully they are all working.
from PIL import Image, ImageDraw




class MakePNG():
    def __init__(self,p1_list,p2_list,p3_list):
        self.p1_list = p1_list
        self.p2_list = p2_list
        self.p3_list = p3_list
        self.include_weather_reading = False
        self.im = None
        self.dr = None
        self.p_length = 240
        self.p_height = 130
        self.p_upper_left_x = 35
        self.p_upper_left_y = 45
        self.spacing = 10

    def _get_weather(self):
        '''
        Get the current weather report.  If there is > 50% chance of rain,
        change the include_weather_reading property to True.  This will cause
        any readings that are set to be watered from the color red to orange.
        '''
        pass
    def _draw_planters(self):
        # Draw the three planters onto the canvas.
        # This planter has it's upper left corner at pixel 45,45.
        # It is 285-45 = 240px wide, 175-45 = 130 px high
        x0 = self.p_upper_left_x
        y0 = self.p_upper_left_y
        x1 = x0 + self.p_length
        y1 = y0 + self.p_height
        self.dr.rectangle( ( (x0,y0),(x1,y1) ),outline = "black",fill='white')
        x0 = x0 + x1 + self.spacing
        x1 = x0 + self.p_length
        y1 = y0 + self.p_height
        self.dr.rectangle( ( (x0,y0),(x1,y1) ),outline = "black",fill='white')
        x0 = self.p_upper_left_x + int(self.p_length/2)
        y0 = self.p_upper_left_y + self.p_height + self.spacing
        x1 = x0 + self.p_length
        y1 = y0 + self.p_height
        self.dr.rectangle( ( (x0,y0),(x1,y1) ),outline = "black",fill='white')

    def _draw_readings(self):
        pass


    def _make_drawing(self):
        self.im = Image.new('RGB', (600,400), "white")
        self.dr = ImageDraw.Draw(self.im)
        # There are three planters
        self._draw_planters()
        self._draw_readings()


    def make_png(self,filename='moisture_readings.png'):
        '''
        Use the moisture readings for each planter to make a PNG that is
        mailed to us.  The PNG gives us a quick visual on whether to
        water.
        '''
        self._make_drawing()
        self.im.save(filename)
