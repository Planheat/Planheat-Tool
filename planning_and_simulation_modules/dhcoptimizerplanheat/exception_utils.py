

class DHCOptimizerException(Exception):
    """Main exception for the DHC Optimizer plugin."""

    def __init__(self, data):
        Exception.__init__(self, data)
        self.data = data

    def show_in_message_bar(self, iface):
        """Show current message in a message bar in the given QGIS interface."""
        iface.messageBar().clearWidgets()
        iface.messageBar().pushMessage("Error", self.data, level=1, duration=0)
