from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from queue import Queue
from threading import Lock

# WebDriver pool class to manage ChromeDriver instances
class WebDriverPool:
    def __init__(self, pool_size=5, version=None, headless=True):
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()
        self.version = version
        self.headless = headless

        # Initialize the pool with ChromeDriver instances
        for _ in range(pool_size):
            self.pool.put(self._create_driver())

    # Private method to create a new WebDriver instance
    def _create_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
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
                # Otherwise, put the driver back in the pool
                self.pool.put(driver)

    # Shutdown the pool and close all drivers
    def shutdown_pool(self):
        while not self.pool.empty():
            driver = self.pool.get()
            driver.quit()