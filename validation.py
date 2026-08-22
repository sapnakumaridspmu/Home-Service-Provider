
class Validation:
    def empty(self,frmList):
        for frm in frmList:
            if frm=='':
                return True    

    def checkDigit(self,data):
        if(not data.isdigit()):
            return True

    def checkAlpha(self,data):
        # Allow letters and single spaces (for full names like "Hello World"),
        # but not digits or symbols. Reject empty/whitespace-only names too.
        stripped = data.strip()
        if stripped == '':
            return True
        if not stripped.replace(' ', '').isalpha():
            return True

    def checkMobileLength(self,data):
        length = len(data)
        if(length!=10):
            return True