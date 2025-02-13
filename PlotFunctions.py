def plot_sigle_line(x, y, Fig_size, Fig_title, x_label, y_label, x_lim, y_lim, colour, save=False):
    '''
    Create a simple line plot.

    Parameters:
    - x         : array-like, the x coordinates of the line plot. 
    - y         : array-like, the y coordinates of the line plot.
    - Fig_size  : a tuple with two items. 
    - Fig_title : str, the title of the plot.
    - x_label   : str, the label of the x axis.
    - y_label   : str, the label of the y axis. 
    - x_lim     : a tuple with two items.
    - y_lim     : a tuple with two items. 
    - colour    : str, the color of the plot.
    - save      : bool, specify whether save the plot. The default is False. 
    '''
    import pylab as plt
    
    # Create the plot and line 
    fig,ax=plt.subplots(figsize=Fig_size) 
    plot=ax.plot(x, y, color = colour, label=y_label) 
    
    ax.set_xlabel(x_label) 
    ax.set_ylabel(y_label)
    ax.set_title(Fig_title) 
    
    lines = plot 
    labels = [l.get_label() for l in lines] 
    
    ax.set_xlim(x_lim) 
    ax.set_ylim(y_lim) 

    if save: 
        plt.savefig('Plot_{plotname}.png'.format(plotname = Fig_title))

    plt.show()
    

def plot_dual_line(x1, y1, x2, y2, Fig_size = (10,6), Fig_title = '', x_label = '', y1_label = '', y2_label = (), x_lim = (), y1_lim = (), y2_lim = (), colour1 ='k', colour2 ='k', save=False, font_size=12, title_size=14, legend_size=10):
    '''
    Create a simple line plot with two y variables

    Parameters:
    - x1        : array-like, the x coordinates of the first line plot(x1).
    - x2         : array-like, the x coordinates of the second line plot(x2).
    - y1        : array-like, the y coordinates of the first line plot(y1).
    - y2        : array-like, the y coordinates of the second line plot(y2).
    - Fig_size  : a tuple with two items. 
    - Fig_title : str, the tile of the plot.
    - x_label   : str, the label of the x axis.
    - y1_label  : str, the label of the y1 axis.
    - y2_label  : str, the label of the y2 axis 
    - x_lim     : a tuple with two items.
    - y1_lim    : a tuple with two items.
    - y2_lim    : a tuple with two items. 
    - colour1   : str, the color of the x-y1 plot.
    - colour2   : str, the color of the x-y2 plot.
    - save      : bool, specify whether save the plot. The default is False.
    - font_size : int, the font size of the labels. The default is 12.
    - title_size: int, the font size of the title. The default is 14.
    - legend_size: int, the font size of the legend. The default is 10.
    '''
    import pylab as plt

    # plot signals
    fig, ax1 = plt.subplots(figsize=Fig_size)  # create a plot to allow for dual y-axes plotting 
    plot1 = ax1.plot(x1, y1, color=colour1, label=y1_label)  # plot Isosbestic signal on left y-axis 
    
    ax2 = plt.twinx()  # create a right y-axis, sharing x-axis on the same plot 
    plot2 = ax2.plot(x2, y2, color=colour2, label=y2_label)  # plot GCaMP signal on right y-axis
    
    ax1.set_xlim(x_lim) 
    ax1.set_ylim(y1_lim)
    ax2.set_ylim(y2_lim)
    ax1.set_xlabel(x_label, fontsize=font_size)
    ax1.set_ylabel(y1_label, color=colour1, fontsize=font_size)
    ax2.set_ylabel(y2_label, color=colour2, fontsize=font_size)
    ax1.set_title(Fig_title, fontsize=title_size)
    
    lines = plot1 + plot2 
    labels = [l.get_label() for l in lines]  # get legend labels 
    legend = ax1.legend(lines, labels, loc='lower right', bbox_to_anchor=(1, 1), fontsize=legend_size)  # add legend
    
    if save: 
        plt.savefig('Plot_{plotname}.png'.format(plotname=Fig_title))
    
    plt.show()

