
class Branch:
    
    def __init__(self):
        self.PFAE = 31
        self.MORALES = 32

    def get_mandatory_docs(self, branchid):
        print("get_mandatory_docs -> branch :" + str(branchid))
        if branchid == self.PFAE:
            return '(24, 2, 3, 4, 28, 29, 5)'
            
        if branchid == self.MORALES:
            return '(24, 2, 3, 30, 31, 5, 37)'


    def get_NAMES_TYPE_DOCUMENTS(self, branchid):
        print("get_NAMES_TYPE_DOCUMENTS -> branch :" + str(branchid))
        if branchid == self.PFAE:
            return {
                "24": "selfie",
                "2": "ineFrontal",
                "3": "ineAnverso",
                "4": "compDomicilio",
                "28": "cedulaFiscal",
                "29": "compDomicilioPFAE",
                "5": "compCuenta"
            }
            
        if branchid == self.MORALES:
            return {
                "24": "selfie",
                "2" : "ineFrontal",
                "3" : "ineAnverso",
                "30": "actacontitutiva",
                "31": "poderes",
                 "5" : "compCuenta",
                "37" : "repcredito_especial"
            }