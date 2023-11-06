import tkinter as tk
from tkinter import ttk
from functools import partial
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import matplotlib.pyplot as plt
from shape_callbacks import shape_create_deadstart, interparc
import numpy as np

class App:
    """
    CLASS: App
    DESCRIPTION: 
    """

    def __init__(self):
        """
        METHOD: __init__
        DESCRIPTION:                
        """        

        # define root window
        self.root = tk.Tk()
        self.define_root_window()                              
                             
        # create notebook with tabs
        notebook = ttk.Notebook(self.root)   
        tab1 = ttk.Frame(notebook)        
        tab2 = ttk.Frame(notebook)
        notebook.add(tab1, text='tab1')
        notebook.add(tab2, text='tab2')
        notebook.pack(expand=1, fill='both')

        # add panels for shape parameter inputs
        self.shape_params = {}
        self.add_shape_params_panel(tab1)
        self.add_shape_points_panel(tab1)
        self.add_segs_panel(tab1)

        # add plot axes
        plot_frame = tk.Frame(tab1)
        plot_frame.pack(side='left', anchor='nw', padx=10)
        self.add_plot_axes(plot_frame)    

        # plot shape
        self.plot_new_bry()


    def add_segs_panel(self, parent):
         
        # panel to hold segment parameter widgets
        panel = tk.LabelFrame(parent, text='Control segments', highlightbackground="gray", highlightthickness=2)
        panel.pack(side='left', anchor='nw', padx=10, pady=10)
        
        # initialize segment parameters
        seg_keys = ['nsegs', 'seglength', 'theta0', 'rc', 'zc', 'a', 'b']
        seg_key_labels = ['# segs', 'seg_length', 'theta0', 'ellipse_r0', 'ellipse_z0', 'ellipse_a', 'ellipse_b']

        self.seg_params = {}
        self.seg_params['rc']        = tk.StringVar(value='1.75')
        self.seg_params['zc']        = tk.StringVar(value='0')
        self.seg_params['a']         = tk.StringVar(value='0.15')
        self.seg_params['b']         = tk.StringVar(value='0.2')
        self.seg_params['seglength'] = tk.StringVar(value='6')
        self.seg_params['nsegs']     = tk.StringVar(value='40')
        self.seg_params['theta0']    = tk.StringVar(value='0')
        
        # assign widgets for each segment parameter
        for i, (key, key_label) in enumerate(zip(seg_keys, seg_key_labels)):
            label = tk.Label(panel, text=key_label)
            label.grid(row=i, column=1)
            entry = tk.Entry(panel, bd=5, width=10, textvariable=self.seg_params[key])                
            entry.bind('<Return>', self.plot_new_bry)                                    
            entry.grid(row=i, column=3)
        
        # manual control segments
        rowstart = i
        label = tk.Label(panel, text='\n\nManual control segments')
        label.grid(row=rowstart+1, column=1, columnspan=2)
        for (i,text) in enumerate(['R0', 'Z0', 'Rf', 'Zf']):
            label = tk.Label(panel, text=text)
            label.grid(row=rowstart+2, column=i)

        rowstart += 3
        self.seg_params['n_manual_segs'] = 8
        for i in range(self.seg_params['n_manual_segs']):
            keys = [f'seg{i}_R0', f'seg{i}_Z0', f'seg{i}_Rf', f'seg{i}_Zf']

            for (col, key) in enumerate(keys):
                self.seg_params[key] = tk.StringVar(value='nan')
                entry = tk.Entry(panel, bd=5, width=3, textvariable=self.seg_params[key])        
                entry.bind('<Return>', self.plot_new_bry)                                    
                entry.grid(row=rowstart+i, column=col)
        

    def tkdict2dict(self, tkdict):
        d = {}
        for key in tkdict.keys():
            try:
                dum = tkdict[key].get()
                d[key] = float(dum)   # convert to numeric if possible
            except:
                d[key] = np.nan       # otherwise, nan
        return d
    
    def gen_segs(self):
        p = self.tkdict2dict(self.seg_params)
        th = np.linspace(0, 2*np.pi, 200) + p['theta0']

        rin = p['rc'] + p['a'] * np.cos(th)
        zin = p['zc'] + p['b'] * np.sin(th)
        rout = p['rc'] + p['seglength'] * p['a'] * np.cos(th)
        zout = p['zc'] + p['seglength'] * p['b'] * np.sin(th)
        
        rout, zout = interparc(rout, zout, int(p['nsegs']))
        idx = []
        for (ro,zo) in zip(rout,zout):
            dist2 = (rin-ro)**2 + (zin-zo)**2
            idx.append(np.argmin(dist2))
        
        idx = np.asarray(idx)
        segs = np.vstack((rin[idx], zin[idx], rout, zout)).T

        return segs

    def plot_segs(self, ax):

        # plot manual segs
        n = self.seg_params['n_manual_segs']
        segs = np.empty((n,4))
        for i in range(n):
            keys = [f'seg{i}_R0', f'seg{i}_Z0', f'seg{i}_Rf', f'seg{i}_Zf']
            for j, key in enumerate(keys):
                dum = self.seg_params[key].get()
                try:
                    segs[i,j] = float(dum)   # convert to numeric if possible
                except:
                    segs[i,j] = np.nan       # otherwise, nan

        ax.plot(segs[:,[0,2]].T, segs[:,[1,3]].T, c='gray', linewidth=0.5)

        # plot parametrized segs
        segs2 = self.gen_segs()
        ax.plot(segs2[:,[0,2]].T, segs2[:,[1,3]].T, c='gray', linewidth=0.5)
                         
  


    def plot_limiter(self, ax):
        rl = [1.26900, 1.26900, 1.26400, 1.43320, 1.38590, 1.38510, 1.29490, 1.32000, 1.44070, 1.44070, 1.50930, 1.57080, 1.57000, 1.72000, 1.72000, 1.84000, 1.84000, 1.69500, 1.65850, 1.65750, 1.64490, 1.84000, 2.03000, 2.03003, 2.08782, 2.13957, 2.18574, 2.22676, 2.26302, 2.30393, 2.33804, 2.36602, 2.38980, 2.40771, 2.42020, 2.42757, 2.43000, 2.42757, 2.42020, 2.40771, 2.38980, 2.36602, 2.33804, 2.30393, 2.26302, 2.22676, 2.18574, 2.13957, 2.08782, 2.03003, 2.03000, 1.84000, 1.64490, 1.65750, 1.65850, 1.69500, 1.84000, 1.84000, 1.72000, 1.72000, 1.57000, 1.57080, 1.50930, 1.44070, 1.44070, 1.32000, 1.29490, 1.38510, 1.38590, 1.43320, 1.26400, 1.26900, 1.26900]
        zl = [0.00000, -0.50000, -0.50000, -1.05920, -1.11600, -1.11540, -1.22360, -1.21000, -1.20900, -1.21000, -1.20900, -1.29640, -1.29700, -1.51000, -1.57500, -1.57500, -1.38000, -1.38000, -1.21770, -1.21790, -1.16190, -1.04000, -0.87000, -0.87000, -0.81543, -0.76087, -0.70630, -0.65173, -0.59717, -0.52571, -0.45426, -0.38280, -0.30624, -0.22968, -0.15312, -0.07656, 0.00000, 0.07656, 0.15312, 0.22968, 0.30624, 0.38280, 0.45426, 0.52571, 0.59717, 0.65173, 0.70630, 0.76087, 0.81543, 0.87000, 0.87000, 1.04000, 1.16190, 1.21790, 1.21770, 1.38000, 1.38000, 1.57500, 1.57500, 1.51000, 1.29700, 1.29640, 1.20900, 1.21000, 1.20900, 1.21000, 1.22360, 1.11540, 1.11600, 1.05920, 0.50000, 0.50000, 0.00000]
        ax.plot(rl, zl, linewidth=1.5, color='black')     

    def add_plot_axes(self, parent): 
        """
        METHOD: plot
        DESCRIPTION: 
        """       

        self.fig = Figure(figsize = (6,6), dpi = 100) 
        self.axs = [None]*3
        self.axs[0] = self.fig.add_subplot(2,2,(1,3)) 
        self.axs[1] = self.fig.add_subplot(2,2,2) 
        self.axs[2] = self.fig.add_subplot(2,2,4) 

        for i in range(3):            
            self.axs[i].grid(visible=True)            
            if i == 0:
                self.axs[i].set_ylabel('Z [m]', fontsize=12)
            if i in (0,2):
                self.axs[i].set_xlabel('R [m]', fontsize=12)
            if i == 1:
                self.axs[i].xaxis.set_ticklabels([])

        self.axs[0].set_xlim((1.2, 2.5))
        self.axs[0].set_ylim((-1.7, 1.7))
        self.axs[1].set_xlim((1.3, 1.85))
        self.axs[1].set_ylim((1.1, 1.6))
        self.axs[2].set_xlim((1.3, 1.85))
        self.axs[2].set_ylim((-1.6, -1.1))

        self.fig.tight_layout()
        
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)   
        self.canvas.draw() 
        # placing the canvas on the Tkinter window 
        self.canvas.get_tk_widget().pack() 
    
        # creating the Matplotlib toolbar 
        toolbar = NavigationToolbar2Tk(self.canvas, parent) 
        toolbar.update() 
        self.canvas.get_tk_widget().pack()


   
    def add_shape_params_panel(self, parent):
        """
        METHOD: add_shape_params_panel
        DESCRIPTION:                
        """        

        # panel to hold shape parameter widgets
        shp_frame = tk.LabelFrame(parent, text='Shape parameters', highlightbackground="gray", highlightthickness=2)
        shp_frame.pack(side='left', anchor='nw', padx=10, pady=10)
            
        # initialize shape parameters
        shape_keys = ['R0','Z0','a','k','triu','tril','squo','squi','sqlo','sqli','c_xplo','c_xpup']
        shape_key_labels = ['Rcenter', 'Zcenter', 'Minor radius', 'Elongation', 'Triangularity upper', 'Triangularity lower',
                           'Squareness up/out', 'Squareness up/in', 'Squareness lo/out', 'Squareness lo/in', 'Xpt_coeff lower', 
                           'Xpt_coeff upper']
        
        self.shape_params['R0']   = tk.StringVar(value='1.8451')
        self.shape_params['Z0']   = tk.StringVar(value='0.0')
        self.shape_params['a']    = tk.StringVar(value='0.5631')
        self.shape_params['k']    = tk.StringVar(value='2.0314')
        self.shape_params['triu'] = tk.StringVar(value='0.59')
        self.shape_params['tril'] = tk.StringVar(value='0.59')
        self.shape_params['squo'] = tk.StringVar(value='-0.22')
        self.shape_params['squi'] = tk.StringVar(value='-0.37')
        self.shape_params['sqlo'] = tk.StringVar(value='-0.22')
        self.shape_params['sqli'] = tk.StringVar(value='-0.37')
        self.shape_params['c_xplo'] = tk.StringVar(value='0.07')
        self.shape_params['c_xpup'] = tk.StringVar(value='0.07') 

        
        # assign widgets for each shape parameter
        for i, (key, key_label) in enumerate(zip(shape_keys, shape_key_labels)):
            label = tk.Label(shp_frame, text=key_label)
            label.grid(row=i, column=2)

            entry = tk.Entry(shp_frame, 
                                bd=5, 
                                width=10, 
                                textvariable=self.shape_params[key])                
            entry.bind('<Return>', self.plot_new_bry)                                    
            entry.grid(row=i, column=3)

    def add_shape_points_panel(self, parent):
        """
        METHOD: add_shape_params_panel
        DESCRIPTION:                
        """        

        # panel to hold shape parameter widgets
        shp_frame = tk.LabelFrame(parent, text='Manual points', highlightbackground="gray", highlightthickness=2)
        shp_frame.pack(side='left', anchor='nw', padx=10, pady=10)

        # Add entries for individual (r,z) points
        # x-points
        self.shape_params['rx1'] = tk.StringVar(value='1.513')
        self.shape_params['zx1'] = tk.StringVar(value='1.144')
        self.shape_params['rx2'] = tk.StringVar(value='1.513')
        self.shape_params['zx2'] = tk.StringVar(value='-1.144')
        self.shape_params['rx3'] = tk.StringVar(value='nan')
        self.shape_params['zx3'] = tk.StringVar(value='nan')
        self.shape_params['rx4'] = tk.StringVar(value='nan')
        self.shape_params['zx4'] = tk.StringVar(value='nan')

        # general control points
        self.shape_params['r1'] = tk.StringVar(value='1.32')
        self.shape_params['z1'] = tk.StringVar(value='1.21')
        self.shape_params['r2'] = tk.StringVar(value='1.32')
        self.shape_params['z2'] = tk.StringVar(value='-1.21')
        self.shape_params['r3'] = tk.StringVar(value='1.57')
        self.shape_params['z3'] = tk.StringVar(value='1.3')
        self.shape_params['r4'] = tk.StringVar(value='1.57')
        self.shape_params['z4'] = tk.StringVar(value='-1.3')
        self.shape_params['r5'] = tk.StringVar(value='1.66')
        self.shape_params['z5'] = tk.StringVar(value='1.52')
        self.shape_params['r6'] = tk.StringVar(value='1.66')
        self.shape_params['z6'] = tk.StringVar(value='-1.52')
        self.shape_params['r7'] = tk.StringVar(value='nan')
        self.shape_params['z7'] = tk.StringVar(value='nan')
        self.shape_params['r8'] = tk.StringVar(value='nan')
        self.shape_params['z8'] = tk.StringVar(value='nan')
        

        rkeys = ['rx' + str(i+1) for i in range(4)] + ['r' + str(i+1) for i in range(8)] 
        zkeys = ['zx' + str(i+1) for i in range(4)] + ['z' + str(i+1) for i in range(8)]

        for i, (rkey, zkey) in enumerate(zip(rkeys, zkeys)):

            label = tk.Label(shp_frame, text=rkey)
            label.grid(row=i, column=1)

            entry = tk.Entry(shp_frame, 
                                bd=5, 
                                width=4, 
                                textvariable=self.shape_params[rkey])                
            entry.bind('<Return>', self.plot_new_bry)                                    
            entry.grid(row=i, column=2)

            label = tk.Label(shp_frame, text=zkey)
            label.grid(row=i, column=3)

            entry = tk.Entry(shp_frame, 
                                bd=5, 
                                width=4, 
                                textvariable=self.shape_params[zkey])                
            entry.bind('<Return>', self.plot_new_bry)                                    
            entry.grid(row=i, column=4)

            
    def plot_new_bry(self, event=None):
        """
        METHOD: plot_new_bry
        DESCRIPTION:                
        """        
        # convert values form Tk-formatted shape_params to a normal python dict
        s = self.tkdict2dict(self.shape_params)

        # create boundary shape from params
        [rb, zb] = shape_create_deadstart(s)

        # plot boundary shape
        for i in range(len(self.axs)):
            ax = self.axs[i]
            
            # remove old lines
            for artist in ax.lines + ax.collections:
                artist.remove()
            
            # plot limiter and new shape
            self.plot_limiter(ax)
            ax.plot(rb, zb, linewidth=1, color='red')   
            
            for k in range(8):
                rkey = 'r' + str(k+1)
                zkey = 'z' + str(k+1)
                ax.scatter(s[rkey], s[zkey], s=30, c='red', alpha=1, marker='d')

            for k in range(4):
                rkey = 'rx' + str(k+1)
                zkey = 'zx' + str(k+1)
                ax.scatter(s[rkey], s[zkey], s=50, c='red', alpha=1, marker='x')

            self.plot_segs(ax)

        self.canvas.draw()                       
  

    def set_entry_text(self, entry, text):
        """
        METHOD: set_entry_text
        DESCRIPTION:                
        """                
        entry.delete('0', 'end')
        entry.insert('0', text)


    def define_root_window(self):
        """
        METHOD: define_root_window
        DESCRIPTION:                
        """                
        self.root.title('Shape Editor')              
        
        # center the window when opened
        w = 1400                            # width for the root window
        h = 800                             # height for the root window
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight() # height of the screen   
        x = (ws/2) - (w/2)                  # calculate x and y coordinates for the window
        y = (hs/2) - (h/2)    
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))              

def main():     
    app = App()
    app.root.mainloop()

if __name__ == '__main__':
    main()
