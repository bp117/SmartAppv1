import { Component, OnInit, Input, OnDestroy }   from '@angular/core';

import { FormData }                              from '../data/formData.model';
import { FormDataService }                       from '../data/formData.service';

@Component ({
    selector:     'mt-wizard-personal'
    ,templateUrl: '../personal/personal.component.html'
})

export class PersonalComponent implements OnInit, OnDestroy {
    title = 'Please tell us about yourself.';
    @Input() formData: FormData;
    public idTypes = [
         { value: '', display: 'Select' },
    { value: 'ssn', display: 'Social Security Number' },
    { value: 'taxpayerID', display: 'Individual Taxpayer ID Number' },
    { value: 'NA', display: 'Not Available' }
    
  ];

    public phonetypes = [
          { value: '', display: 'Select' },
    { value: 'cell', display: 'Cell' },
    { value: 'home', display: 'Home' },
    { value: 'work', display: 'Work' }
    
  ]
    constructor(private formDataService: FormDataService) {
    }

    ngOnInit() {
        this.formData = this.formDataService.getData();
        console.log('Personal feature loaded!');
    }

    ngOnDestroy() {
        this.formDataService.setData(this.formData);
    }
}

