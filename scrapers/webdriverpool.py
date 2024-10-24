from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from queue import Queue
from threading import Lock

# WebDriver pool class to manage ChromeDriver instances
class WebDriverPool:
    def __init__(self, pool_size=1, version=None, path=None, headless=True):
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()
        self.version = version
        self.headless = headless
        self.path = path

        # Initialize the pool with ChromeDriver instances
        for _ in range(pool_size):
            self.pool.put(self._create_driver())

    # Private method to create a new WebDriver instance
    def _create_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
            chrome_options.add_argument("--no-sandbox")  # Disable sandboxing (required in some Linux environments)
            chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
            chrome_options.add_argument("--disable-setuid-sandbox")

        chrome_options.binary_location = self.path
        
        # If version is not provided, use the latest version of ChromeDriver
        if self.version:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager(driver_version=self.version).install()),
                options=chrome_options
            )
        else:
            # Automatically install and use the latest version of ChromeDriver
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
        return driver

    # Get a WebDriver instance from the pool
    def get_driver(self):
        with self.lock:
            if self.pool.empty():
                # If pool is empty, create a new WebDriver instance
                return self._create_driver()
            return self.pool.get()

    # Return a WebDriver instance back to the pool
    def return_driver(self, driver):
        with self.lock:
            if self.pool.full():
                # If pool is full, quit the driver
                driver.quit()
            else:
                # Check if there are still open windows
                if len(driver.window_handles) > 1:
                    driver.close()  # Only close the current tab if there are multiple tabs
                else:
                    driver.quit()  # If there's only one tab, quit the driver
                    driver = self._create_driver()  # Create a new driver to return to the pool
                
                # Open a blank page to avoid errors in future interactions
                driver.get("about:blank")
                self.pool.put(driver)


    # Shutdown the pool and close all drivers
    def shutdown_pool(self):
        while not self.pool.empty():
            driver = self.pool.get()
            driver.quit()