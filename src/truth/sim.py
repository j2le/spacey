
class sim(object):
    def __init__(self):
        # propagation time step
        self.dt = 1
        self.time = 0
        self.parent_body = "earth"

    def update(self):

      # update time
      self.time = self.time + self.dt
         

