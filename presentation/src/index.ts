import {FrontendHandler} from "./FrontendHandler";
import {PresentationCommunicator} from "./PresentationCommunicator";

/*
 * The initialization loop.
 * As mqtt needs a loop to receive messages this gets a bit complicated.
 * First the mqtt client gets initialized by first creating a new instance.
 * Then the frontend gets initialized and the instance is then passed to the communicator as an instance.
 * This is necessary, as the mqtt messages have to be passed on to the frontend later on.
 */
PresentationCommunicator.getInstance().init().then(function () {
    let fh = new FrontendHandler();
    fh.init().then(function () {
        PresentationCommunicator.getInstance().setFrontend(fh)
    })
});


