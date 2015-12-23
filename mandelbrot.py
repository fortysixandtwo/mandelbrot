import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import mpl
from gmpy2 import mpc, mpz, mpq, mpfr
import numpy as np
import random
import time


def timeIt(func, parms=None):
    t = time.time()
    if parms is None:
        func()
    else:
        func(parms)
    return time.time()-t

def getColorFromIterations(fraction):
    # fraction is number of iterations divided by maximum iteration number
    # neat blue->violet transition
    c = int(fraction * 255)
    m = 255
    y = 0
    k = 0
    if (fraction == 1.):
        k = 255
    return QColor.fromCmyk(c,m,y,k)

def f(z,c): #Iterationsvorschrift
    return z*z+c

class MandelMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, mandel, parent=None, width=5, height=4, dpi=100):
        self.mandel = mandel
        if (mandel.__class__.__name__ != "MandelbrotSet"):
            print('mandel var {}  is not of type MandelbrotSet!')
            exit(1)
        fig = Figure(figsize=(width,height),dpi=dpi)
        self.plt = fig.add_subplot(111)
        self.plt.hold(False)
        self.compute_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicyExpanding, QSizePolicyExpanding)
        FigureCanvas.updateGeometry(self)

    def compute_figure(self):
        cmap = mpl.colors.LinearSegmentedColormap.from_list('blue velvet', ['fuchsia', 'darkblue', 'black'], self.maxIterations)
        extent = (self.mandel.xmin, self.mandel.xmax, self.mandel.ymin, self.mandel.ymax)
        self.plt.imshow(self.mandel.data, cmap=cmap, extent=extent)

class MandelbrotSet():
    def __init__(self, _xmin, _xmax, _ymin, _ymax, _Nx, _Ny, _maxRadius, _maxIterations):
        self.xmin = mpfr(_xmin)
        self.xmax = mpfr(_xmax)
        self.ymin = mpfr(_ymin)
        self.ymax = mpfr(_ymax)
        self.Nx = _Nx
        self.Ny = _Ny
        self.maxRadius = _maxRadius
        self.maxIterations = _maxIterations
        self.x = np.linspace(self.xmin, self.xmax, self.Nx)
        self.y = np.linspace(self.ymin, self.ymax, self.Ny)
        self.data = np.zeros((self.Nx, self.Ny), dtype=np.int64)
        self.recalculate()

    def recalculate(self):
        # set precision based on min, max and N?
        # gmpy2.get_context().precision = 53 (std)
        self.x = np.linspace(self.xmin, self.xmax, self.Nx)
        self.y = np.linspace(self.ymin, self.ymax, self.Ny)
        self.data = np.zeros((self.Nx, self.Ny))
        maxRad2 = self.maxRadius * self.maxRadius
        for i in range(self.Nx):
          for j in range(self.Ny):
            nIter = 0
            z = mpc(self.x[i], self.y[j])
            c = z
            while (nIter < self.maxIterations) and ((z.real*z.real+z.imag*z.imag) <= maxRad2):
              z = f(z,c)
              nIter += 1
            self.data[i,j] = nIter
              
"""1 Year Old. Redo is overdue      
class MandelbrotWidget(QWidget):
    def __init__(self, parent=None):
        super(MandelbrotWidget,self).__init__(parent)

        self.setMinimumSize(640,480)
        self.xmin = -1.5
        self.xmax = 0.5
        self.ymin = -1.5
        self.ymax = 1.5
        self.Nmax = 100
        self.maxradius = 2.
        #self.timeInfo = timeInfo
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        #self.parent = parent
        self.reDraw = True
        self.picture = QPicture()
        self.renderTime = 0.

    def update_parent(self):
        self.parent().renderTimeInfo.setText("Rendering done in {}s".format(self.renderTime))
        self.parent().minxNumBox.setText("{}".format(self.xmin))
        self.parent().maxxNumBox.setText("{}".format(self.xmax))
        self.parent().minyNumBox.setText("{}".format(self.ymin))
        self.parent().maxyNumBox.setText("{}".format(self.ymax))
        self.parent().iterationNumBox.setText("{}".format(self.Nmax))
        self.parent().maxradiusNumBox.setText("{}".format(self.maxradius))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()
            #print("Event {}/{} Origin {}/{}".format(event.x(),event.y(),self.origin.x(),self.origin.y()))
            dx = (self.xmax-self.xmin)/self.size().width()
            dy = (self.ymax-self.ymin)/self.size().height()
            #print("Dx {} Dy {}".format(self.rubberBand.size().width(), self.rubberBand.size().height()))
            if event.x() < self.origin.x():
                self.xmin += event.x() * dx
                self.xmax = self.xmin + self.origin.x() * dx
            else:
                self.xmin += self.origin.x() * dx
                self.xmax = self.xmin + event.x() * dx
            if event.y() > self.origin.y():
                self.ymin += (self.size().height() - event.y()) * dy
                self.ymax = self.ymin + (self.size().height() - self.origin.y()) * dy
            else:
                self.ymin += (self.size().height() - self.origin.y()) * dy
                self.ymax = self.ymin + (self.size().height() - event.y()) * dy
            self.reDraw = True

    def paintEvent(self, event):
        start_time = time.time()
        if self.reDraw:
            painter = QPainter()
            painter.begin(self.picture)
            painter.setRenderHint(QPainter.Antialiasing)
        #print(self.size())
            dx = (self.xmax-self.xmin)/self.size().width()
            dy = (self.ymax-self.ymin)/self.size().height()
            z0 = 0.
            maxcol = 2**24
            dcol = maxcol / self.Nmax
            for x in range(self.size().width()):
                for y in range(self.size().height()):
                    c = self.xmin + x*dx + 1j * (self.ymin + y*dy)
                    z = 0.
                    running = True
                    i = 0
                    while running:
                        z = f(z,c)
                        i += 1
                        if (i == self.Nmax) or (np.abs(z) > self.maxradius):
                            running = False
                            pen = QPen(QColor(0,0,0))
                            pen.setWidth(1)
                            pen.setColor(QColor((self.Nmax-i)*dcol))
                #pen.setColor(QColor(255,255,0))
                #if (i == self.Nmax):
                    painter.setPen(pen)
                    painter.drawPoint(x,y)

            painter.end()
            self.renderTime = time.time()-start_time
            self.reDraw = False
            self.update_parent()
            painter.begin(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPicture(0,0,self.picture)
            painter.end()
        else:
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPicture(0,0,self.picture)
            painter.end()
            self.parent().renderTimeInfo.setText("redrawed in {}s".format(time.time()-start_time))

class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        # top frame objects
        self.iterationLabel = QLabel("Max iterations:")
        self.iterationNumBox = NumBox("100")
        self.maxradiusLabel = QLabel("Max radius:")
        self.maxradiusNumBox = NumBox("2")
        self.minxLabel = QLabel("min x:")
        self.maxxLabel = QLabel("max x:")
        self.minyLabel = QLabel("min y:")
        self.maxyLabel = QLabel("max y:")
        self.minxNumBox = NumBox("-3")
        self.maxxNumBox = NumBox("-3")
        self.minyNumBox = NumBox("3")
        self.maxyNumBox = NumBox("3")
        self.updateButton = QPushButton("&Update")
        self.updateButton.clicked.connect(self.update_mandelbrot)
        self.renderTimeInfo = QLineEdit("Rendering done in [time]")
        self.renderTimeInfo.setReadOnly(True)

        # layout, mb overcomplicated, but im a knoob
        #vLayout1 = QVBoxLayout()
        #vLayout2 = QVBoxLayout()
        #vLayout1.addWidget(self.iterationLabel)
        #vLayout1.addWidget(self.iterationNumBox)
        #vLayout2.addWidget(self.maxradiusLabel)
        #vLayout2.addWidget(self.maxradiusNumBox)


        # main Layout and MandelbrotWidget
        mainLayout = QVBoxLayout()
        topframeLayout = QGridLayout()
        #mainLayout.addWidget(nameLabel, 0, 0)

        topframeLayout.addWidget(self.iterationLabel,0,0)
        topframeLayout.addWidget(self.iterationNumBox,0,1)
        topframeLayout.addWidget(self.maxradiusLabel,0,2)
        topframeLayout.addWidget(self.maxradiusNumBox,0,3)
        topframeLayout.addWidget(self.minxLabel,1,0)
        topframeLayout.addWidget(self.minxNumBox,1,1)
        topframeLayout.addWidget(self.maxxLabel,1,2)
        topframeLayout.addWidget(self.maxxNumBox,1,3)
        topframeLayout.addWidget(self.minyLabel,2,0)
        topframeLayout.addWidget(self.minyNumBox,2,1)
        topframeLayout.addWidget(self.maxyLabel,2,2)
        topframeLayout.addWidget(self.maxyNumBox,2,3)

        #topframeLayout.addLayout(vLayout2)
        mainLayout.addLayout(topframeLayout)
        mainLayout.addWidget(self.updateButton)
        self.mandelWidget = MandelbrotWidget(self)
        mainLayout.addWidget(self.mandelWidget)
        mainLayout.addWidget(self.renderTimeInfo)

        self.setLayout(mainLayout)
        self.resize(self.sizeHint())
        self.setWindowTitle("Mandelbrot with PyQt5 and gmpy2")

        # event handling, TODO window resize, mouse scroll for zoom



    def update_mandelbrot(self):
        #print("self.update_mandelbrot() called")
        self.mandelWidget.xmin = float(self.minxNumBox.text())
        self.mandelWidget.xmax = float(self.maxxNumBox.text())
        self.mandelWidget.ymin = float(self.minyNumBox.text())
        self.mandelWidget.ymax = float(self.maxyNumBox.text())
        self.mandelWidget.maxradius = float(self.maxradiusNumBox.text())
        self.mandelWidget.Nmax = float(self.iterationNumBox.text())
        self.mandelWidget.reDraw = True
        #self.mandelWidget.repaint()


class NumBox(QLineEdit):
    def __init__(self, args=None):
        super(NumBox,self).__init__(args)
        self.textChanged.connect(self.isNumText)

    def isNumText(self): #TODO Allow "-" character!
        isNum = False
        while (not isNum) and (len(self.text()) > 0):
            try:
                num = float(self.text())
                isNum = True
            except Exception as inst:
                print("type: {} args: {}".format(type(inst),inst.args))
                self.setText(self.text()[:-1]) #deletes last character, assuming first characters are valid (numerical)
        return isNum


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    screen = Form()
    screen.show()

    sys.exit(app.exec_())
"""
