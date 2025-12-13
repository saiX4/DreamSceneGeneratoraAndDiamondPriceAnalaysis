import pandas as pd
import wx
from wx.lib.pubsub import pub
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import seaborn as sns
import numpy as np

# --- Constants & Configuration ---
LIGHT_BLUE = wx.Colour(173, 216, 230)
FILE_PATH = "diamonds.csv"
CAT_ORDERS = {
    'cut': ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal'],
    'color': ['J', 'I', 'H', 'G', 'F', 'E', 'D'],
    'clarity': ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF']
}
PLOTS = {
    'scatter': {'title': "Price vs. Carat (Colored by Cut)", 'x': 'carat', 'y': 'price', 'type': 'scatter', 'hue': 'cut'},
    'bar': {'title': "Average Price by Cut Quality", 'x': 'cut', 'y': 'price', 'type': 'bar', 'order': CAT_ORDERS['cut']}
}
COUNT_PLOTS = [
    {'col': 'color', 'order': CAT_ORDERS['color'], 'title': 'Count by Color Grade (J-D)', 'plot_type': 'count'},
    {'col': 'clarity', 'order': CAT_ORDERS['clarity'], 'title': 'Count by Clarity Grade (I1-IF)', 'plot_type': 'count'},
    {'col': 'cut', 'order': CAT_ORDERS['cut'], 'title': 'Count by Cut Quality (Fair-Ideal)', 'plot_type': 'count'},
    {'col': 'depth', 'order': None, 'title': 'Count Distribution by Depth (%)', 'plot_type': 'hist'}
]

df = None # Global DataFrame

# --- Data Core ---

def load_data(path):
    """Loads and cleans the diamond dataset."""
    global df
    try:
        df = pd.read_csv(path).drop(columns=['Unnamed: 0'], errors='ignore')
        initial_rows = len(df)
        df = df[(df[['x', 'y', 'z']] != 0).all(axis=1)]
        cleaned_rows = len(df)

        for col, order in CAT_ORDERS.items():
            df[col] = pd.Categorical(df[col], categories=order, ordered=True)

        pub.sendMessage("DATA_LOADED", success=True, 
                        message=f"✅ Data loaded! Initial: {initial_rows:,}, Cleaned: {cleaned_rows:,} diamonds.")
    except Exception as e:
        pub.sendMessage("DATA_LOADED", success=False, message=f"❌ Error: {e}.")
        df = None

def get_stats():
    """Returns the descriptive statistics DataFrame."""
    return df[['carat', 'price']].describe().T if df is not None else None

# --- GUI Class ---

class DiamondFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(1000, 700))
        self.SetIcon(wx.Icon())
        
        self.panel = wx.Panel(self, size=self.GetSize())
        self.panel.SetBackgroundColour(LIGHT_BLUE)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText(f"Ready. Loading {FILE_PATH}...")
        self.current_plot_widget = None

        self._setup_ui()
        self.Show()

        pub.subscribe(self._on_data_loaded, "DATA_LOADED")
        wx.CallLater(100, lambda: load_data(FILE_PATH))
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _add_text(self, label, parent, sizer=None, size=14, style=wx.FONTWEIGHT_NORMAL, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5):
        """Helper to create and add common StaticText widgets."""
        text = wx.StaticText(parent, label=label)
        text.SetBackgroundColour(LIGHT_BLUE)
        text.SetFont(wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, style))
        (sizer or self.main_sizer).Add(text, 0, flag, border)
        return text

    def _create_btn(self, label, handler, sizer):
        """Helper to create and add a button."""
        btn = wx.Button(self.left_panel, label=label)
        btn.Bind(wx.EVT_BUTTON, handler)
        btn.Disable()
        sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 5)
        return btn

    def _setup_ui(self):
        self._add_text("ANALYSIS: Diamond Price and Quality Data", self.panel, size=12, style=wx.FONTWEIGHT_BOLD)

        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        load_btn = wx.Button(self.panel, label="Load Diamond Data")
        load_btn.Bind(wx.EVT_BUTTON, self._on_reload_data)
        control_sizer.Add(load_btn, 0, wx.ALL | wx.CENTER, 5)
        self.main_sizer.Add(control_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Splitter setup
        self.splitter = wx.SplitterWindow(self.panel) 
        self.splitter.SetBackgroundColour(LIGHT_BLUE)
        self.splitter.SetMinimumPaneSize(20)
        
        # Left Panel (Controls and Summary)
        self.left_panel = wx.Panel(self.splitter)
        self.left_panel.SetBackgroundColour(LIGHT_BLUE)
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_panel.SetSizer(self.left_sizer)

        # Right Panel (Plot)
        self.right_panel = wx.Panel(self.splitter)
        self.right_panel.SetBackgroundColour(LIGHT_BLUE)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_panel.SetSizer(self.right_sizer)

        self._setup_left_controls()
        self._setup_right_plot_area()

        self.splitter.SplitVertically(self.left_panel, self.right_panel, 350)
        self.main_sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizerAndFit(self.main_sizer)
        self.panel.Layout()

    def _setup_left_controls(self):
        # Summary Controls
        self._add_text("Data Summary & Controls", self.left_panel, self.left_sizer, size=14, style=wx.FONTWEIGHT_BOLD)
        self.summary_btn = self._create_btn("Show Summary Statistics", self._on_show_summary, self.left_sizer)
        
        # Summary Area Panel
        # FIXED: Removed background_color from constructor
        self.summary_area = wx.Panel(self.left_panel)
        self.summary_area.SetBackgroundColour(LIGHT_BLUE)
        self.summary_sizer = wx.BoxSizer(wx.VERTICAL)
        self.summary_area.SetSizer(self.summary_sizer)
        self.summary_sizer.AddStretchSpacer(1)
        self.left_sizer.Add(self.summary_area, 1, wx.EXPAND | wx.ALL, 10)

        # Visualization Controls
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        self._add_text("Visualizations & Report", self.left_panel, button_sizer, size=12, style=wx.FONTWEIGHT_BOLD, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.scatter_btn = self._create_btn("Carat vs. Price Scatter Plot", lambda evt: self._update_plot(PLOTS['scatter']), button_sizer)
        self.bar_btn = self._create_btn("Average Price by Cut Quality Bar Plot", lambda evt: self._update_plot(PLOTS['bar']), button_sizer)
        self.count_plots_btn = self._create_btn("Categorical Count Plots", self._on_show_count_plots, button_sizer)
        self.report_btn = self._create_btn("Diamond Quality Report", self._on_show_quality_report, button_sizer)

        self.left_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.left_sizer.Layout()

    def _setup_right_plot_area(self):
        self.plot_placeholder = self._add_text("Visualization Area", self.right_panel, self.right_sizer, size=14, style=wx.FONTWEIGHT_BOLD, flag=wx.ALL | wx.CENTER)
        self.right_sizer.SetItemMinSize(self.plot_placeholder, -1, 400)
        self.current_plot_widget = self.plot_placeholder

    def _on_close(self, event):
        """Handle the window close event for clean exit."""
        self._cleanup_plot_area() 
        event.Skip() 
        self.Destroy() 

    def _cleanup_plot_area(self):
        """Cleans up the current Matplotlib/report widget."""
        if self.current_plot_widget:
            if isinstance(self.current_plot_widget, FigureCanvasWxAgg):
                plt.close(self.current_plot_widget.figure) 
            self.current_plot_widget.Destroy()
            self.current_plot_widget = None
            self.right_sizer.Layout()

    def _on_reload_data(self, event):
        """Triggers a reload of the default CSV file and clears summary area."""
        self.status_bar.SetStatusText(f"Reloading data from: {FILE_PATH}...")
        self.summary_sizer.Clear(True)
        self.summary_sizer.AddStretchSpacer(1)
        self.summary_area.Layout()
        load_data(FILE_PATH)

    def _on_data_loaded(self, success, message):
        """Updates GUI status and enables/disables buttons."""
        self.status_bar.SetStatusText(message)
        for btn in [self.summary_btn, self.scatter_btn, self.bar_btn, self.count_plots_btn, self.report_btn]:
            btn.Enable(success)

    def _on_show_quality_report(self, event):
        """Generates and displays a text report."""
        if df is None: return self.status_bar.SetStatusText("Data not loaded.")
        self._cleanup_plot_area()
        
        report = (
            "DIAMOND QUALITY AND PRICE DRIVERS\n" "================================\n\n"
            "Prices are driven by '4 Cs': Carat, Cut, Color, and Clarity.\n\n"
            "1. CARAT (Weight): Most significant factor. Price scales exponentially.\n\n"
            "2. CUT (Quality): Proportions maximize brilliance.\n"
            "• Grades: Fair < Good < Very Good < Premium < Ideal. Higher grade = Higher price.\n\n"
            "3. COLOR (Whiteness): Absence of color (D is best).\n"
            "• Grades: D (Colorless) down to J (Faint Yellow). D, E, F command premiums.\n\n"
            "4. CLARITY (Internal Flaws/Inclusions): Flawlessness.\n"
            "• Grades: I1 < ... < VS2 < VS1 < VVS2 < VVS1 < IF (Flawless).\n\n"
            "GOOD QUALITY: Balances aesthetics and value (Cut: Ideal/Premium, Color: D-G, Clarity: VS2-IF)."
        )

        report_display = self._add_text(report, self.right_panel, self.right_sizer, size=11, flag=wx.EXPAND | wx.ALL, border=15)
        self.current_plot_widget = report_display
        self.right_sizer.Layout()
        self.status_bar.SetStatusText("Diamond Quality Report Generated.")

    def _create_list_ctrl(self, data):
        """Helper to create and populate the wx.ListCtrl."""
        # Note: wx.ListCtrl also does not take 'background_color'
        list_ctrl = wx.ListCtrl(self.summary_area, style=wx.LC_REPORT) 
        list_ctrl.SetBackgroundColour(LIGHT_BLUE)
        
        list_ctrl.InsertColumn(0, "Feature", width=80)
        for i, col in enumerate(data.columns):
            list_ctrl.InsertColumn(i + 1, col.capitalize(), width=70, format=wx.LIST_FORMAT_RIGHT)
        
        for i, (index, row) in enumerate(data.iterrows()):
            list_ctrl.InsertItem(i, index.capitalize())
            for j, val in enumerate(row):
                formatted = f"{val:,.2f}" if isinstance(val, (int, float, np.floating)) else str(val)
                list_ctrl.SetItem(i, j + 1, formatted)
        
        list_ctrl.SetMinSize((-1, 25 + (len(data) * 22) + 15)) 
        return list_ctrl

    def _on_show_summary(self, event):
        """Displays descriptive statistics in a wx.ListCtrl."""
        summary = get_stats()
        if summary is None: return self.status_bar.SetStatusText("Data not loaded.")

        self.summary_sizer.Clear(True)
        list_ctrl = self._create_list_ctrl(summary)
        self.summary_sizer.Add(list_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        footer_text = f"Total Diamonds: {len(df):,} | Mean Price: ${df['price'].mean():,.2f}"
        self._add_text(footer_text, self.summary_area, self.summary_sizer, size=10, flag=wx.ALL | wx.CENTER)

        self.summary_sizer.Layout()
        self.left_sizer.Layout()

    def _update_plot(self, config):
        """Generates and embeds a Matplotlib plot based on config."""
        if df is None: return self.status_bar.SetStatusText("Data not loaded.")
        self._cleanup_plot_area()

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

        if config['type'] == 'scatter':
            sns.scatterplot(x=config['x'], y=config['y'], hue=config['hue'], data=df, ax=ax, alpha=0.6, s=10)
            ax.set(xlabel=f"{config['x'].capitalize()} Weight", ylabel=f"{config['y'].capitalize()} ($)")
        elif config['type'] == 'bar':
            sns.barplot(x=config['x'], y=config['y'], data=df, ax=ax, order=config['order'], palette='viridis')
            ax.set(xlabel=f"{config['x'].capitalize()} Quality", ylabel=f"Average {config['y'].capitalize()} ($)")

        ax.set_title(config['title'])
        fig.tight_layout()
        
        canvas = FigureCanvasWxAgg(self.right_panel, -1, fig)
        self.right_sizer.Add(canvas, 1, wx.EXPAND | wx.ALL, 5)
        self.current_plot_widget = canvas
        self.right_sizer.Layout()
        self.status_bar.SetStatusText(f"{config['title']} Generated.")

    def _on_show_count_plots(self, event):
        """Generates and embeds four side-by-side count/distribution plots."""
        if df is None: return self.status_bar.SetStatusText("Data not loaded.")
        self._cleanup_plot_area()

        fig, axes = plt.subplots(2, 2, figsize=(9, 7))
        axes = axes.flatten()
        
        for i, item in enumerate(COUNT_PLOTS):
            ax = axes[i]
            if item['plot_type'] == 'count':
                sns.countplot(x=item['col'], data=df, order=item['order'], ax=ax, palette='Blues_d')
                ax.set_xlabel(f"{item['col'].capitalize()} Grade")
            else: # 'hist' for depth
                sns.histplot(x=item['col'], data=df, ax=ax, bins=25, kde=False, color='skyblue')
                ax.set_xlabel("Depth Percentage")

            ax.set_ylabel("Count of Diamonds")
            ax.set_title(item['title'], fontsize=10)
            
        fig.tight_layout(pad=3.0)

        canvas = FigureCanvasWxAgg(self.right_panel, -1, fig)
        self.right_sizer.Add(canvas, 1, wx.EXPAND | wx.ALL, 5)
        self.current_plot_widget = canvas
        self.right_sizer.Layout()
        self.status_bar.SetStatusText("4-Panel Categorical Count Plots Generated.")

class DiamondApp(wx.App):
    def OnInit(self):
        DiamondFrame(None, title="Diamond Price Analysis Tool (wxPython)").Centre()
        return True

if __name__ == '__main__':
    app = DiamondApp()
    app.MainLoop()