import { Component, OnInit, Input, OnDestroy,ViewChild,ElementRef,NgZone }   from '@angular/core';

import { FormDataService }                       from '../data/formData.service';
import { AgmCoreModule, MapsAPILoader } from 'angular2-google-maps/core';

@Component ({
    selector:     'mt-wizard-address'
    ,templateUrl: '../address/address.component.html'
})

export class AddressComponent implements OnInit, OnDestroy {
    title = 'Where do you live?';
    @Input() formData;
     @ViewChild("search")
  public searchElementRef: ElementRef;

    constructor(private formDataService: FormDataService,private mapsAPILoader: MapsAPILoader,
    private ngZone: NgZone) {
        
    }

    ngOnInit() {
        this.formData = this.formDataService.getData();
            //load Places Autocomplete
    this.mapsAPILoader.load().then(() => {
      let autocomplete = new google.maps.places.Autocomplete(this.searchElementRef.nativeElement, {
        types: ["address"]
      });
      autocomplete.addListener("place_changed", () => {
        this.ngZone.run(() => {
          //get the place result
          let place: google.maps.places.PlaceResult = autocomplete.getPlace();
  
          //verify result
          if (place.geometry === undefined || place.geometry === null) {
            return;
          }
           var details = place.formatted_address.split(",");
           console.log(details[0]);
           this.formData.street = details[0];
          this.formData.city = details[1];
          this.formData.state = details[2].replace(/\d+/g,'');
          
        });
      });
    });
        console.log('Address feature loaded!');
    }

    ngOnDestroy() {
        this.formDataService.setData(this.formData);
    }
}