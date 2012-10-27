	hs.align = 'center';
	hs.transitions = ['expand', 'crossfade'];
	hs.fadeInOut = true;
	hs.dimmingOpacity = 0.8;
	hs.wrapperClassName = 'borderless floating-caption';
	hs.captionEval = 'this.thumb.alt';
	hs.marginBottom = 100 // make room for the floating caption and thumbstrip
	hs.numberPosition = 'caption';
	hs.lang.number = '%1/%2';


	// Add the slideshow providing the controlbar and the thumbstrip
	hs.addSlideshow({
		//slideshowGroup: 'group1',
		interval: 5000,
		repeat: false,
		useControls: true,
		fixedControls: 'fit',
		overlayOptions: {
			position: 'bottom center',
//			relativeTo: 'viewport',
	//		offsetY: -50,
			hideOnMouseOut: true

		},
		thumbstrip: {
			position: 'bottom center',
			mode: 'horizontal',
			relativeTo: 'viewport'
		}
	});

	/*
	// Add the simple close button
	hs.registerOverlay({
		html: '<div class="closebutton" onclick="return hs.close(this)" title="Close"></div>',
		position: 'top right',
		fade: 2 // fading the semi-transparent overlay looks bad in IE
	});
	*/
