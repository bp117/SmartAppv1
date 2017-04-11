import { Component, OnInit, Input, OnDestroy }   from '@angular/core';

import { FormDataService }                       from '../data/formData.service';

@Component ({
    selector:     'mt-wizard-work'
    ,templateUrl: '../work/work.component.html'
})

export class WorkComponent implements OnInit, OnDestroy {
    title = 'What do you do?';
    @Input() formData;
      public empStatuses = [
     { value: '', display: 'Select' },
    { value: 'employed', display: 'Employed' },
    { value: 'homemaker', display: 'Home Maker' },
    { value: 'Retired', display: 'Retired' }
    
  ];
    constructor(private formDataService: FormDataService) {
    }

    ngOnInit() {
        this.formData = this.formDataService.getData();
        console.log('Work feature loaded!');
    }

    ngOnDestroy() {
        this.formDataService.setData(this.formData);
    }
}