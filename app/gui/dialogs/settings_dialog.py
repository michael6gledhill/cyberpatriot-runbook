from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtWidgets import QLineEdit as QLineEditWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from sqlalchemy import create_engine
from sqlalchemy import text

class SettingsDialog(QDialog):
    """Dialog to configure backend database connection."""

    def __init__(self, parent=None, current_url: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Backend Settings")
        self.setMinimumWidth(420)

        self.host = QLineEdit()
        self.user = QLineEdit()
        self.password = QLineEdit()
        # Use explicit enum to satisfy type checker
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.dbname = QLineEdit()
        self.port = QLineEdit()
        self.port.setText("3306")

        # Try to parse current_url if provided
        if current_url.startswith("mysql+pymysql://"):
            try:
                # crude parse: mysql+pymysql://user:pass@host:port/db
                rest = current_url.split("//", 1)[1]
                creds, hostdb = rest.split("@", 1)
                user, pwd = creds.split(":", 1)
                hostport, db = hostdb.split("/", 1)
                if ":" in hostport:
                    host, port = hostport.split(":", 1)
                else:
                    host, port = hostport, "3306"
                self.host.setText(host)
                self.port.setText(port)
                self.user.setText(user)
                self.password.setText(pwd)
                self.dbname.setText(db)
            except Exception:
                pass
        else:
            # Prefill sensible defaults provided by the user
            self.host.setText("192.168.3.127")
            self.port.setText("3306")
            self.user.setText("cp_user")
            self.password.setText("your-strong-password")
            self.dbname.setText("cyberpatriot_runbook")

        layout = QVBoxLayout()
        for label, widget, placeholder in [
            ("Host/IP:", self.host, "SERVER_IP"),
            ("Port:", self.port, "3306"),
            ("Username:", self.user, "cp_user"),
            ("Password:", self.password, "your-strong-password"),
            ("Database:", self.dbname, "cyberpatriot_runbook"),
        ]:
            layout.addWidget(QLabel(label))
            widget.setPlaceholderText(placeholder)
            layout.addWidget(widget)

        btns = QHBoxLayout()
        test_btn = QPushButton("Test Connection")
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btns.addWidget(test_btn)
        btns.addStretch()
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)
        self.setLayout(layout)

        test_btn.clicked.connect(self._test_connection)
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_database_url(self) -> str:
        host = self.host.text().strip()
        port = self.port.text().strip() or "3306"
        user = self.user.text().strip()
        pwd = self.password.text()
        db = self.dbname.text().strip()
        return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"

    def _test_connection(self):
        url = self.get_database_url()
        try:
            engine = create_engine(url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            QMessageBox.information(self, "Success", "Connection succeeded.")
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))
