import { Component, OnInit, Input }   from '@angular/core';

import { FormDataService }            from './data/formData.service';

@Component ({
    selector:     'multi-step-wizard-app'
    ,templateUrl: './app.component.html'
})

export class AppComponent implements OnInit {
    title = 'SmartApp';
    @Input() formData;
    
    constructor(private formDataService: FormDataService) {
    }

    ngOnInit() {
        this.formData = this.formDataService.getData();
        console.log(this.title + ' loaded!');
    }
}