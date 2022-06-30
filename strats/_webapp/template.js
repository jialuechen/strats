

;(function(templateJS, window, document, undefined) {

    function isArray(input) {
        return Object.prototype.toString.call(input) === '[object Array]';
    }
    
    var ext_modifiers = {};
    templateJS.extend = function(modifier, callback) {
        ext_modifiers[modifier] = callback;
    };

    function run_modifiers(value, modifiers, undefined) {
        if (value === '' || value === undefined || value === null) {
            if (modifiers[0] === "allow_null") {
                return '';
            }
            return '-';
        }

        if (!modifiers || modifiers.length == 0) {
            return value;
        }

        value = value.toString();

        for (var i = 0; i < modifiers.length; i++) {
            var modifier = modifiers[i].toLowerCase();

            if (modifier === "capitalize") value = value.toLowerCase().replace(/^.|\s\S/g,function(a){return a.toUpperCase();});
            if (modifier === "uppercase")  value = value.toUpperCase();
            if (modifier === "lowercase")  value = value.toLowerCase();
            if (modifier === "nozero" && value.toString() === "0") value = "";
            if (modifier === "clean_url")  {
                value = value.split("://");
                if (value.length === 2) {
                    value = value[1];
                } else {
                    value = value[0];
                }
                value = value.replace("www.", "");
                if (value.slice(0 -1) == '/') {
                    value = value.substring(0, value.length-1);
                }
            }
            if (modifier === "unix2date")  value = new Date(value*1000)

            if (modifier === "format_number") value = format_number(value, 2);
            if (modifier === "format_decimal") value = format_number(value, 2);
            if (modifier === "format_number_as_word") value = format_number_as_word(value);
            if (modifier === "format_int") value = format_number(value, 0);

            if (modifier === "link") {
                var replacedText, replacePattern1, replacePattern2, replacePattern3;

                // URLs starting with http://, https://, or ftp://
                replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
                replacedText = value.replace(replacePattern1, '<a href="$1" target="_blank">$1</a>');

                // URLs starting with "www." (without // before it, or it'd re-link the ones done above).
                replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
                replacedText = replacedText.replace(replacePattern2, '$1<a href="http://$2" target="_blank">$2</a>');

                // Change email addresses to mailto:: links.
                replacePattern3 = /(([a-zA-Z0-9\-\_\.])+@[a-zA-Z\_]+?(\.[a-zA-Z]{2,6})+)/gim;
                replacedText = replacedText.replace(replacePattern3, '<a href="mailto:$1">$1</a>');

                value = replacedText;
            }

            // external modifiers
            if (ext_modifiers.hasOwnProperty(modifier)) {
                value = ext_modifiers[modifier](value);
            }
        };

        // return
        return value;
    }
   
try {
    jQuery.extend({ "templateJS": function(templateId, data, callback) {
        return templateJS.parse(templateId, data, callback);
    }});
} catch(er) {}