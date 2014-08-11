import syslog

class Logger:

    
    def __init__(self, ident):
        """ 
        Given a identity string and a min priority string create a logger 
        instance. The priority string must be one of ...
        EMERG, ALERT, CRIT, ERR, WARNING, NOTICE, INFO, DEBUG
        
        args    : ident ...        loggers identity
                  min_priority ... min report priority EMERG, ALERT, CRIT, ERR, 
                                   WARNING, NOTICE, INFO or DEBUG
        excepts : 
        return  : none
        """
        
        self.ident = ident
    
        
    def log(self, msg, priority):
        """
        Log an message string with a certain priority string. If that priority
        is greater than the pre-defined min priority log the message to 
        /var/log/messages.  The priority string must be one of EMERG, ALERT, 
        CRIT, ERR, WARNING, NOTICE, INFO, DEBUG
        
        args    : msg ...      message to be logged
                  priority ... priority of the msg EMERG, ALERT, CRIT, ERR, 
                               WARNING, NOTICE, INFO or DEBUG
        excepts : 
        return  : none
        """
        
        syslog.openlog(self.ident , syslog.LOG_PID, (syslog.LOG_ALERT | syslog.LOG_USER)) 
        syslog.syslog(priority,msg)
        syslog.closelog()
        
    def d(self,msg):
        self.log(msg,syslog.LOG_DEBUG)

    def e(self,msg):
        self.log(msg,syslog.LOG_ERR)

    def a(self,msg):
        self.log(msg,syslog.LOG_ALERT)
    
    def c(self,msg):
        self.log(msg,syslog.LOG_CRIT)

    def w(self,msg):
        self.log(msg,syslog.LOG_WARNING)

    def n(self,msg):
        self.log(msg,syslog.LOG_NOTICE)

    def i(self,msg):
        self.log(msg,syslog.LOG_INFO)
