from copy import copy

from LaserCommandConstants import *
from RasterPlotter import RasterPlotter, X_AXIS, TOP, BOTTOM, Y_AXIS, RIGHT, LEFT, UNIDIRECTIONAL
from svgelements import Length, SVGImage, SVGElement, Shape

VARIABLE_NAME_NAME = 'name'
VARIABLE_NAME_SPEED = 'speed'
VARIABLE_NAME_POWER = 'power'
VARIABLE_NAME_OVERSCAN = 'overscan'
VARIABLE_NAME_DRATIO = 'd_ratio'
VARIABLE_NAME_RASTER_STEP = 'raster_step'
VARIABLE_NAME_RASTER_DIRECTION = 'raster_direction'


class LaserOperation(list):
    """
    Default object defining any operation done on the laser.
    Laser operations are a type of list and should contain SVGElement based objects
    """

    def __init__(self, *args, **kwargs):
        list.__init__(self)
        self.status_value = "Queued"
        self.speed = None
        self.power = None
        self.dratio_custom = False
        self.dratio = None
        self.acceleration_custom = False
        self.acceleration = None
        try:
            self.speed = float(kwargs['speed'])
        except ValueError:
            pass
        except KeyError:
            pass
        try:
            self.power = float(kwargs['power'])
        except ValueError:
            pass
        except KeyError:
            pass
        try:
            self.dratio = float(kwargs['dratio'])
        except ValueError:
            pass
        except KeyError:
            pass
        try:
            self.dratio_custom = bool(kwargs['dratio_custom'])
        except ValueError:
            pass
        except KeyError:
            pass

        try:
            self.acceleration = int(kwargs['acceleration'])
        except ValueError:
            pass
        except KeyError:
            pass
        try:
            self.acceleration_custom = bool(kwargs['acceleration_custom'])
        except ValueError:
            pass
        except KeyError:
            pass

        if len(args) == 1:
            obj = args[0]
            if isinstance(obj, SVGElement):
                self.set_properties(obj.values)
                self.append(obj)
            elif isinstance(obj, LaserOperation):
                self.speed = obj.speed
                self.power = obj.power
                self.dratio_custom = obj.dratio_custom
                self.dratio = obj.dratio
                self.acceleration_custom = obj.acceleration_custom
                self.acceleration = obj.acceleration

                for element in obj:
                    element_copy = copy(element)
                    self.append(element_copy)

    def __str__(self):
        parts = []
        parts.append("speed=%f" % self.speed)
        parts.append("power=%f" % self.power)
        if self.dratio is not None:
            parts.append("dratio=%f" % self.dratio)
        return "Unknown Operation: (%s)" % ", ".join(parts)

    def __copy__(self):
        return LaserOperation(self)

    @property
    def time_estimate(self):
        return "Unknown"

    @property
    def status(self):
        return self.status_value

    def has_same_properties(self, values):
        """
        Checks the object to see if there are changed properties from the otherwise set values of these attributes.
        :param values: property to check
        :return:
        """
        if 'speed' in values and values['speed'] is not None:
            if self.speed != float(values['speed']):
                return False
        if 'power' in values and values['power'] is not None:
            if self.power != float(values['power']):
                return False
        if 'dratio' in values and values['dratio'] is not None:
            if self.dratio != float(values['dratio']):
                return False
        if 'acceleration' in values and values['acceleration'] is not None:
            if self.acceleration != int(values['acceleration']):
                return False
        return True

    def set_properties(self, values):
        """
        Sets the new value based on the given object. Assuming the object has the properties in question.
        :param values:
        :return:
        """
        if 'speed' in values and values['speed'] is not None:
            self.speed = float(values['speed'])
        if 'power' in values and values['power'] is not None:
            self.power = float(values['power'])
        if 'dratio' in values and values['dratio'] is not None:
            self.dratio = float(values['dratio'])
        if 'acceleration' in values and values['acceleration'] is not None:
            self.acceleration = int(values['acceleration'])


class RasterOperation(LaserOperation):
    """
    Defines the default raster operation to be done and the properties needed.
    """

    def __init__(self, *args, **kwargs):
        LaserOperation.__init__(self, *args, **kwargs)
        if self.speed is None:
            self.speed = 150.0
        if self.power is None:
            self.power = 1000.0
        self.raster_step = 1
        try:
            self.raster_step = int(kwargs['raster_step'])
        except ValueError:
            pass
        except KeyError:
            pass
        self.raster_direction = 0
        try:
            self.raster_direction = int(kwargs['raster_direction'])
        except ValueError:
            pass
        except KeyError:
            pass
        self.unidirectional = False
        self.overscan = 20
        try:
            self.overscan = int(kwargs['overscan'])
        except ValueError:
            pass
        except KeyError:
            pass
        if len(args) == 1:
            obj = args[0]
            if isinstance(obj, SVGElement):
                self.set_properties(obj.values)
            elif isinstance(obj, RasterOperation):
                self.raster_step = obj.raster_step
                self.raster_direction = obj.raster_direction
                self.unidirectional = obj.unidirectional
                self.overscan = obj.overscan

    def __str__(self):
        parts = []
        parts.append("speed=%s" % Length.str(self.speed))
        parts.append("step=%d" % self.raster_step)
        parts.append("direction=%d" % self.raster_direction)
        parts.append("overscan=%d" % self.overscan)
        return "Raster: (%s)" % ", ".join(parts)

    def __copy__(self):
        return RasterOperation(self)

    @property
    def time_estimate(self):
        estimate = 0
        for e in self:
            if isinstance(e, SVGImage):
                try:
                    step = e.raster_step
                except AttributeError:
                    step = 1
                estimate += (e.image_width * e.image_height * step) / (39.3701 * self.speed)
        hours, remainder = divmod(estimate, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "%s:%s:%s" % (int(hours), str(int(minutes)).zfill(2), str(int(seconds)).zfill(2))

    @property
    def status(self):
        return self.status_value

    def set_properties(self, values):
        if 'raster_step' in values and values['raster_step'] is not None:
            self.raster_step = int(values['raster_step'])
        if 'raster_direction' in values and values['raster_direction'] is not None:
            self.raster_direction = int(values['raster_direction'])
        if 'unidirectional' in values and values['unidirectional'] is not None:
            self.unidirectional = bool(values['unidirectional'])
        if 'overscan' in values and values['overscan'] is not None:
            self.overscan = int(values['overscan'])

    def has_same_properties(self, values):
        if 'raster_step' in values and values['raster_step'] is not None:
            if self.raster_step != int(values['raster_step']):
                return False
        if 'raster_direction' in values and values['raster_direction'] is not None:
            if self.raster_direction != int(values['raster_direction']):
                return False
        if 'unidirectional' in values and values['unidirectional'] is not None:
            if self.unidirectional != bool(values['unidirectional']):
                return False
        if 'overscan' in values and values['overscan'] is not None:
            if self.overscan != int(values['overscan']):
                return False
        return True

    def generate(self):
        yield COMMAND_MODE_RAPID
        yield COMMAND_SET_ABSOLUTE
        yield COMMAND_SET_SPEED, self.speed
        direction = self.raster_direction
        step = self.raster_step
        yield COMMAND_SET_POWER, self.power
        yield COMMAND_SET_D_RATIO, None
        if self.acceleration is not None and self.acceleration_custom:
            yield COMMAND_SET_ACCELERATION, self.acceleration
        else:
            yield COMMAND_SET_ACCELERATION, None

        yield COMMAND_SET_STEP, step
        traverse = 0
        if direction == 0:
            traverse |= X_AXIS
            traverse |= TOP
        elif direction == 1:
            traverse |= X_AXIS
            traverse |= BOTTOM
        elif direction == 2:
            traverse |= Y_AXIS
            traverse |= RIGHT
        elif direction == 3:
            traverse |= Y_AXIS
            traverse |= LEFT
        if self.unidirectional:
            traverse |= UNIDIRECTIONAL

        for svgimage in self:
            if not isinstance(svgimage, SVGImage):
                continue  # We do not raster anything that is not classed properly.
            image = svgimage.image
            width, height = image.size
            mode = image.mode

            if mode != "1" and mode != "P" and mode != "L" and mode != "RGB" and mode != "RGBA":
                # Any mode without a filter should get converted.
                image = image.convert("RGBA")
                mode = image.mode
            if mode == "1":
                def image_filter(pixel):
                    return (255 - pixel) / 255.0
            elif mode == "P":
                p = image.getpalette()

                def image_filter(pixel):
                    v = p[pixel * 3] + p[pixel * 3 + 1] + p[pixel * 3 + 2]
                    return 1.0 - v / 765.0
            elif mode == "L":
                def image_filter(pixel):
                    return (255 - pixel) / 255.0
            elif mode == "RGB":
                def image_filter(pixel):
                    return 1.0 - (pixel[0] + pixel[1] + pixel[2]) / 765.0
            elif mode == "RGBA":
                def image_filter(pixel):
                    return (1.0 - (pixel[0] + pixel[1] + pixel[2]) / 765.0) * pixel[3] / 255.0
            else:
                raise ValueError  # this shouldn't happen.
            m = svgimage.transform
            data = image.load()

            overscan = self.overscan
            if overscan is None:
                overscan = 20
            else:
                try:
                    overscan = int(overscan)
                except ValueError:
                    overscan = 20
            raster = RasterPlotter(data, width, height, traverse, 0, overscan,
                                   m.value_trans_x(),
                                   m.value_trans_y(),
                                   step, image_filter)
            yield COMMAND_MODE_RAPID
            x, y = raster.initial_position_in_scene()
            yield COMMAND_MOVE, x, y
            top, left, x_dir, y_dir = raster.initial_direction()
            yield COMMAND_SET_DIRECTION, top, left, x_dir, y_dir
            yield COMMAND_MODE_PROGRAM
            yield COMMAND_RASTER, raster
        yield COMMAND_MODE_RAPID


class EngraveOperation(LaserOperation):
    """
    Defines the default vector engraving operation. This is intended to mark the
    object being engraved on.
    """

    def __init__(self, *args, **kwargs):
        LaserOperation.__init__(self, *args, **kwargs)
        if self.speed is None:
            self.speed = 35.0
        if self.power is None:
            self.power = 1000.0

    def __str__(self):
        parts = []
        parts.append("speed=%f" % self.speed)
        parts.append("power=%f" % self.power)
        return "Engrave: (%s)" % ", ".join(parts)

    def __copy__(self):
        return EngraveOperation(self)

    @property
    def time_estimate(self):
        estimate = 0
        for e in self:
            if isinstance(e, SVGElement):
                try:
                    length = e.length(error=1e-2, min_depth=2)
                except AttributeError:
                    length = 0
                try:
                    estimate += length / (39.3701 * self.speed)
                except ZeroDivisionError:
                    estimate = float('inf')
        hours, remainder = divmod(estimate, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "%s:%s:%s" % (int(hours), str(int(minutes)).zfill(2), str(int(seconds)).zfill(2))

    def generate(self):
        yield COMMAND_MODE_RAPID
        yield COMMAND_SET_ABSOLUTE
        yield COMMAND_SET_SPEED, self.speed
        yield COMMAND_SET_STEP, 0
        yield COMMAND_SET_POWER, self.power
        if self.dratio is not None and self.dratio_custom:
            yield COMMAND_SET_D_RATIO, self.dratio
        else:
            yield COMMAND_SET_D_RATIO, None
        if self.acceleration is not None and self.acceleration_custom:
            yield COMMAND_SET_ACCELERATION, self.acceleration
        else:
            yield COMMAND_SET_ACCELERATION, None
        try:
            first = abs(self[0]).first_point
            yield COMMAND_MOVE, first[0], first[1]
        except (IndexError, AttributeError):
            pass
        yield COMMAND_MODE_PROGRAM
        for object_path in self:
            plot = abs(object_path)
            yield COMMAND_PLOT, plot
        yield COMMAND_MODE_RAPID


class CutOperation(LaserOperation):
    """
    Defines the default vector cut operation.
    """

    def __init__(self, *args, **kwargs):
        LaserOperation.__init__(self, *args, **kwargs)
        if self.speed is None:
            self.speed = 10.0
        if self.power is None:
            self.power = 1000.0

    def __str__(self):
        parts = []
        parts.append("speed=%f" % self.speed)
        parts.append("power=%f" % self.power)
        return "Cut: (%s)" % ", ".join(parts)

    def __copy__(self):
        return CutOperation(self)

    @property
    def time_estimate(self):
        estimate = 0
        for e in self:
            if isinstance(e, Shape):
                try:
                    length = e.length(error=1e-2, min_depth=2)
                except AttributeError:
                    length = 0
                try:
                    estimate += length / (39.3701 * self.speed)
                except ZeroDivisionError:
                    estimate = float('inf')
        hours, remainder = divmod(estimate, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "%s:%s:%s" % (int(hours), str(int(minutes)).zfill(2), str(int(seconds)).zfill(2))

    def generate(self):
        yield COMMAND_MODE_RAPID
        yield COMMAND_SET_ABSOLUTE
        yield COMMAND_SET_SPEED, self.speed
        yield COMMAND_SET_STEP, 0
        yield COMMAND_SET_POWER, self.power
        if self.dratio is not None and self.dratio_custom:
            yield COMMAND_SET_D_RATIO, self.dratio
        else:
            yield COMMAND_SET_D_RATIO, None
        if self.acceleration is not None and self.acceleration_custom:
            yield COMMAND_SET_ACCELERATION, self.acceleration
        else:
            yield COMMAND_SET_ACCELERATION, None
        try:
            first = abs(self[0]).first_point
            yield COMMAND_MOVE, first[0], first[1]
        except (IndexError, AttributeError):
            pass
        yield COMMAND_MODE_PROGRAM
        for object_path in self:
            plot = abs(object_path)
            yield COMMAND_PLOT, plot
        yield COMMAND_MODE_RAPID


