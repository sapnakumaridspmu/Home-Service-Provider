
class Validation:
    def empty(self,frmList):
        for frm in frmList:
            if frm=='':
                return True    

    def checkDigit(self,data):
        if(not data.isdigit()):
            return 1
            
    def checkMobileLength(self,data):   
        length = len(data) 
        if(length!=10):
            return 1             

    def checkAlpha(self,data):
        if(not data.isalpha()):
            return True

    def checkMobileLength(self,data):
        length = len(data) 
        if(length!=10):
            return True               