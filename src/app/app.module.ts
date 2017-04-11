import { NgModule }           from '@angular/core';
import { BrowserModule }      from '@angular/platform-browser';
import { UIRouterModule }     from "ui-router-ng2";
import { FormsModule }        from '@angular/forms';

/* App Root */
import { AppComponent }       from './app.component';
import { NavbarComponent }    from './navbar/navbar.component';

/* Feature Components */
import { PersonalComponent }  from './personal/personal.component';
import { WorkComponent }      from './work/work.component';
import { AddressComponent }   from './address/address.component';
import { ResultComponent }    from './result/result.component';

/* App Router */
import { UIRouterConfigFn }   from "./app.router";
import { appStates }          from "./app.states";

/* Shared Service */
import { FormDataService }    from './data/formData.service'
import { AgmCoreModule, MapsAPILoader } from 'angular2-google-maps/core';

@NgModule({
    imports:      [ BrowserModule, 
                    FormsModule,
                    UIRouterModule.forRoot({ 
                      states: appStates,
                      useHash: true,
                      config: UIRouterConfigFn
                    }) ,
                    AgmCoreModule.forRoot({
      apiKey: "AIzaSyBB-6vnrKvsddLkJn1IhLRg0dt7maZmX0s",
      libraries: ["places"]
    }),
                  ],
    providers:    [{ provide: FormDataService, useClass: FormDataService }],
    declarations: [ AppComponent, NavbarComponent, PersonalComponent, WorkComponent, AddressComponent, ResultComponent ],
    bootstrap:    [ AppComponent ]
})

export class AppModule {}