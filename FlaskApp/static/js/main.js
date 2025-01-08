let myChannel = "caitlins-pi-channel";
let pubnub;

sendEvent('get_auth_key')

function keepAlive()
{
	fetch('/keep_alive')
	.then(response=> {
		if(response.ok){
			let date = new Date();
			aliveSecond = date.getTime();
			return response.json();
		}
		throw new Error('Server offline');
	})
	.then(responseJson => console.log(responseJson))
	.catch(error => console.log(error));
	setTimeout('keepAlive()', heartbeatRate);
}

const setupPubNub = () =>{
	pubnub = new pubnub({
	publishKey: 'pub-c-2c57a378-e9c5-4a38-b5a9-ca63a5690e3f',
	subscribeKey: 'sub-c-f8634488-8121-483a-97b3-dafd35e24195',
	userId: 'Caitlins_Web_App'
	})

	   // create a local channel
	   const channel = pubnub.channel(appChannel);
	   // create a subscription on the channel
	   const subscription = channel.subscription();
	   // add listener - for the status message (connected or not)
	   pubnub.addListener({
		   status: (s) =>{
			   console.log("Status", s.category)
		   }
	   });
   
	   // add an onMessage listener on the channel - when a message is recieved what do we do with it?
	   subscription.onMessage = (messageEvent) => {
		   handleMessage(messageEvent.message);
	   }
	   // subscribe to the channel
	   subscription.subscribe();
}

const publishMessage = async(message) => {
    const publishPayload = {
        channel: appChannel,
        message : {
            message:message,
        },
    };
    await pubnub.publish(publishPayload);
}

