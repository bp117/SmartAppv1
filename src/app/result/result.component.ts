import { Component, OnInit, Input }   from '@angular/core';

import { FormDataService }            from '../data/formData.service';

@Component ({
    selector:     'mt-wizard-result'
    ,templateUrl: '../result/result.component.html',

})

export class ResultComponent implements OnInit {
    title = 'Thanks for staying tuned!';
    @Input() formData;
    
    constructor(private formDataService: FormDataService) {
    }

    ngOnInit() {
        this.formData = this.formDataService.getData();
        console.log('Result feature loaded!');
    }
  createAndOpenFile(event){
    var stupidExample = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?> <DEAL xmlns:ns1="http://www.w3.org/1999/xlink" xmlns:ns2="http://www.mismo.org/residential/2009/schemas" xmlns:ns3="http://service.wellsfargo.com/entity/USO/2012"> <ASSETS/> <COLLATERALS/> <LOANS/> <PARTIES> <PARTY> <INDIVIDUAL> <NAME> <FirstName>'+this.formData.firstName+'</FirstName> <LastName>'+this.formData.lastName+'</LastName> </NAME> </INDIVIDUAL> <ROLES> <ROLE> <BORROWER> <RESIDENCES> <RESIDENCE> <ADDRESS> <AddressLineText>'+this.formData.street+'</AddressLineText> <CityName>'+this.formData.city+'</CityName> <PostalCode>'+this.formData.zip+'</PostalCode> <StateCode>'+this.formData.state+'</StateCode> </ADDRESS> </RESIDENCE> </RESIDENCES> </BORROWER> </ROLE> </ROLES> <TAXPAYER_IDENTIFIERS> <TAXPAYER_IDENTIFIER> <TaxpayerIdentifierType>'+this.formData.idType+'</TaxpayerIdentifierType> <TaxpayerIdentifierValue>'+this.formData.idNumber+'</TaxpayerIdentifierValue> </TAXPAYER_IDENTIFIER> </TAXPAYER_IDENTIFIERS></PARTY> </PARTIES> </DEAL>';
    
    window.open('data:application/xml,' + encodeURIComponent(stupidExample));
} 

}
