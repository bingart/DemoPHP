<script> /* tracking version */
(function () {
	function _pf_log(content) {if(true){console.log(content);}}
	function _pf_event(category, action, label) {if (typeof ga == "function") { ga('send', 'event', category, action, label, { nonInteraction: true }); }}
	function getQueryStringByName(b){if(_deq.length>1){var a=_deq.match(new RegExp("[?&]"+b+"=([^&]+)","i"));if(a!=null&&a.length>=1){
	function replaceAll(str, find, replace) { return str.replace(new RegExp(find, 'g'), replace); }
	var isBot = /bot|google|baidu|bing|msn|duckduckgo|teoma|slurp|yandex/i.test(navigator.userAgent);
	var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
	var isAdTracking = (location.href.indexOf('?atr=1') > 0);
    jQuery(function($){
		function adBanner(content) {
			var html = $('#content').html();
			var adjs = replaceAll('<div class="code-block code-block-5" style="margin: 8px 0; clear: both;"><script2 async="async" data-cfasync="false" src="//native.propellerads.com/1?z=2045285&eid="></script2></div>', 'script2', 'script');
			$('#content').html();
		}

		function postTracking() {
			var url = '/wp-content/post-tester/tracking.php';
			$.post(
				url,
				{
					url: location.href,
					ua: navigator.userAgent;,
					success: success,
					dataType: dataType
				},
				function( data ) {
					_pf_log('post data:' + data);
				}
			);
		}
		
		$(document).ready(function(){
			if (isAdTracking) {
				adBanner();
				postTracking();
			}
		});
	});
})();
</script>