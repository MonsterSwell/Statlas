(function($){

    var gup = function (name) {
      name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
      var regexS = "[\\?&]"+name+"=([^&#]*)";
      var regex = new RegExp( regexS );
      var results = regex.exec( window.location.href );
      if( results == null ) {
        return false;
      } else {
        return results[1];
      }
    };

  $(function () {

    if(!$.browser.webkit && $("body").hasClass("page-create")) {
      $("#content").before(
        "<div class='browserwarning'>" +
        "<img src='/media/images/warning.png' alt=''>" +
        "Unfortunately, your browser might not fully be supported. " +
        "Statlas works best in Google Chrome or Apple Safari.</div>");
    }

    if($("#map1").length) {
      $.maplayers = {};
      $.maps.init("map1");
      $.statlas.init();
    }

    if($("body").hasClass("page-explore")) {
      $("input").bind('change', function() {
        $("#mapform").submit();
      });
      $("input:checked").parent().css({"font-weight":"bold"});
    }

  });

  $.statlas = $.statlas || {};
  $.extend($.statlas, {
    regioList : [],
    init: function () {
      var that = this;

      if($("body").hasClass("page-create")) {
        this.createInit();
      } else if($("body").hasClass("page-mapdetail")) {
        this.viewInit();
      }
    },
    createInit: function () {
      var that = this;
      $("#id_title").keyup(function() {
        $(".mapholder h2").text($(this).val());
      });

      $("#mapform").bind("submit", function (){
        return false;
      });

      $("#savemap").bind("click", function () {
        that.saveData();
        return false;
      });

      $("#clearUpload").bind("click", function () {
        $(".data-upload input").replaceWith('<input type="file" name="dataupload" id="dataupload" onchange="$.statlas.handleFiles(this.files)">');
        $("#clearUpload").fadeOut();
        $(".data-upload p").slideUp();
        return false;
      });

      // onchange of regioselect
      $("#id_regionset").change(function() {
        if($(this).val()) {
          that.loading();
          that.regioset = $(this).val();
          $.statlas.noInitCallback = false;

          //get regio geojson and load map
          $.maps.loadGeoJson(that.regioset, function () {
            //get datasets for regio
            $.get("/jsdata/regionsets/" + that.regioset + "/datasets.json").success(function (data) {
              var dataselect = "<select id='id_dataset' name='dataset'>"
                             + "<option value=''>---------</option>"
                             + "<option value='empty'>New dataset</option>";
              if(data && data.length) {
                for (option in data) {
                  dataselect += "<option value='"+ data[option].slug +"'>"+ data[option].title+"</option>";
                }
              }
              dataselect += "</select>";

              $(".select-data").find("select").slideUp(function () {
                $(this).remove();
              }).end().append(dataselect).slideDown();

              if(gup("dataset")) {
                $("#id_dataset option[value=" + gup("dataset") + "]").attr("selected","selected").parent().change();
              }

              that.doneLoading();
            });
          });
        } else {
          $(".select-data").slideUp(400, function() {
            $(this).find("select").remove();
          });
        }
      });

      //onchange of dataselect
      $("#id_dataset").live('change', function() {
        if($(this).val()) {
          that.loading();

          $.get("/jsdata/regionsets/" + that.regioset + "/" + $(this).val() + ".json", function (data) {

            //fill in data editor
            var dataEditor = "<ul>";
            for(var i in $.statlas.regioList) {
              var title = $.statlas.regioList[i].cityName,
                  slug = $.statlas.regioList[i].citySlug,
                  value =  data.values[slug]; //Math.random() //"foo"+$.statlas.colorArray[parseInt(10*Math.random(),10)];

              if (title) {
                dataEditor += "<li " + (i % 2 ? "" : "class='even'") + ">"
                         +  "<label for='" + slug + "'>" + title + "</label>"
                         +  "<input type='text' id='" + slug + "' name='" + slug + "' value='" + value + "'/></li>";
              }
            }
            dataEditor += "</ul>";

            // fill in metainfo
            $("#id_title").val(data.meta.title).keyup();
            $("#id_description").val(data.meta.description);
            $("#id_public").attr("checked", data.meta.public);
            that.dataset = {};
            that.dataset.slug = data.meta.dataset || "empty";

            //zoom and pan
            if(data.meta.zoom != "") {
              $.maps.map.zoom(data.meta.zoom);
            }

            if(data.meta.longitude != "" && data.meta.latitude != "") {
              $.maps.map.center({
                lat: data.meta.latitude,
                lon: data.meta.longitude
              });
            }

            that.startDataEditor(dataEditor);
            that.startDataDownload(that.regioset);
            that.doneLoading();
          });
        } else {
          $(".data-editor").slideUp(400, function() {
            $(this).find("ul").remove();
          });
        }
      });


      if(gup("regionset")) {
        $("#id_regionset option[value=" + gup("regionset") + "]").attr("selected","selected").parent().change();
      }
    },
    viewInit: function () {
      var that = this,
          $maps = $.maps;
      that.loading();

      $(".embedbutton").bind("click", function () {
        var link = $(this).attr("href"),
            embed = '<iframe src="' + link + '" scrolling="no" frameborder="0" style="width:300px;height:400px"></iframe>';
        $(".code-example").find("code").text(embed).end().fadeIn(500);
        return false;
      });
      $(".code-example a").bind("click", function () {
        $(this).parent().fadeOut(500);
        return false;
      });

      $(".favbutton").bind("click", function () {
        var $this = $(this),
            link = window.location.href.split("#")[0] + $this.text().toLowerCase() + "/";

        $.getJSON(link, function (data) {
          if(data.status == "success") {
            if($this.text() == "Favorite") {
              $this.text("Unfavorite");
              that.loading("Added to favorites");
            } else {
              $this.text("Favorite");
              that.loading("Removed from favorites");
            }
          } else {
            that.loading("Error: " + data.message);
          }
          setTimeout(that.doneLoading, 4000);
        });
        return false;
      });

      $maps.loadGeoJson(window.mapdetail.regionset, function () {
        $.get(window.mapdetail.dataset, function (data) {
          //zoom and pan
          if(data.meta.zoom != "") {
            $.maps.map.zoom(data.meta.zoom);
          }
          if(data.meta.longitude != "" && data.meta.latitude != "") {
            $.maps.map.center({
              lat: data.meta.latitude,
              lon: data.meta.longitude
            });
          }
          that.dataset = $.statlas.dataset || {};
          that.dataset.slug = data.meta.dataset || "empty";
          that.setMinMax();
          $maps.setColors($.statlas.valobject);
          that.startDataDownload(window.mapdetail.regionset);
          that.doneLoading();
        });
      });
    },
    startDataDownload: function (regio) {
      var that = this;
      $(".data-download").find("a").each( function () {
        var extension = $(this).find("span").text().split(".")[1],
            text = regio + "_" + that.dataset.slug + "." + extension,
            href = "/download/" + regio + "_" + that.dataset.slug + "." + extension;

        $(this).find("span").text(text).end().attr("href", href);
      }).end().slideDown();

      $(".data-upload").slideDown();
    },
    startDataEditor: function (dataEditor) {
      $(".data-editor").find("ul").remove().end().append(dataEditor).slideDown();
      var that = this;
      that.setMinMax();
      $.maps.setColors(that.valobject);
      that.setLink($.statlas.dataset.slug);

      $(".data-editor input").live("blur", function () {
        clearTimeout(window.blinkTimeout);
        $.statlas.blink = false;

        $(this).siblings().css("color","");
        that.setMinMax();

        $.maps.setColors(that.valobject);
        $("#savemap").text("Save this map").show();
      }).unbind("focus").bind("focus", function (e) {
        clearTimeout(window.blinkTimeout);
        $.statlas.blink = true;

        var blink = function ($path, i) {
          var color = ["#777", "#333"];
          $path.css({"fill":color[i]});

          if (i == 0) {
            i = 1;
          } else {
            i = 0;
          }
          var innerfunc= function() {
            blink($path, i);
          };
          if($.statlas.blink) {
            clearTimeout(window.blinkTimeout);
            window.blinkTimeout = setTimeout(innerfunc, 1000);
          }

        };
        blink($("path[name=" + $(this).attr("name") + "]"), 0);

        $(this).siblings().css("color","#000");
      }).live("change", function () {
        $(".data-download p").slideDown();
      });
    },
    setMinMax: function () {
      var that = this;
      that.valarray = [];
      that.valobject = {};

      $(".data-editor input").each(function () {
        val = $(this).val();
        valname = $(this).attr("name");
        that.valobject[valname] = val;

        if(val && !isNaN(val)) {
          that.valarray.push(val);
        }
      });
      that.valcolors = that.makeRandomColors(that.findUniques(that.valobject));
      that.minvalue = Math.min.apply(Math, that.valarray);
      that.maxvalue = Math.max.apply(Math, that.valarray);
    },
    findUniques: function(valobject) {
      var that = this,
          array = [];
      for (object in valobject) {
        if(!(valobject[object] in that.oc(array))) {
          array.push(valobject[object]);
        }
      }
      return array;
    },
    makeRandomColors: function (array) {
      var that = this,
          colors = that.valcolors || {},
          step = 1/array.length,
          hue = 0;

      for(var i=0;i<array.length;i++) {
        if(!colors[array[i]]) {
          colors[array[i]] = "hsl(" + (parseInt(hue*360, 10)) +", 75%, 75%)";
        }
        hue = (hue + step)%1;
      }
      return colors;
    },
    saveData: function () {
      var that = this,
          dataObj = {};

      if(!that.dataset || !that.dataset.slug ||  $("#id_title").val() == "") {
        if($("#id_title").val() == "") {
          that.loading("You need to fill in a title!");
        } else {
          that.loading("Not enough information to save!");
        }

        setTimeout(that.doneLoading, 4000);
        return false;
      }
      dataObj.meta = {};
      dataObj.meta.title = $("#id_title").val();
      dataObj.meta.description = $("#id_description").val();
      dataObj.meta.public = $("#id_public").attr("checked");
      dataObj.meta.zoom = $.maps.map.zoom();
      dataObj.meta.latitude = $.maps.map.center().lat;
      dataObj.meta.longitude = $.maps.map.center().lon;
      dataObj.meta.regionset = $("#id_regionset").val();
      dataObj.meta.dataset = that.dataset.slug;
      dataObj.csrfmiddlewaretoken = $("input[name='csrfmiddlewaretoken']").val();
      dataObj.dataupload = $.statlas.dataupload || "";

      dataObj.values = {};
      for (i in $.statlas.regioList) {
        dataObj.values[$.statlas.regioList[i].citySlug] = document.getElementById($.statlas.regioList[i].citySlug).value;
      }


      that.loading("Saving data...");
      $("#savemap").text("Saving...");

      $.ajax({
        type: "POST",
        data: dataObj,
        dataType: "json",
        url: "/create/save/",
        success: function (data) {
          if(data.status == "success") {
            that.doneLoading();
            that.setLink(data.dataset);

            //update datasets dropdown
            var dataselect = "<option value=''>---------</option>"
                           + "<option value='empty'>Nieuwe dataset</option>";
            if(data && data.data_sets.length) {
              for (option in data.data_sets) {
                dataselect += "<option value='"+ data.data_sets[option].slug +"'>"+ data.data_sets[option].title+"</option>";
              }
            }
            dataselect += "</select>";
            $("#id_dataset").empty().html(dataselect).find("option[value=" + data.dataset + "]").attr("selected","selected").end().change();
            $(".data-download p").slideUp();
            $("#clearUpload").click();
            $("#savemap").text("Map saved!");
          } else {
            that.loading(data.status + ": " + data.message);
          }
        },
        error: function(data, status, error) {
          that.loading("Error!");
          //document.write(data.responseText);
        }
      });
    },
    handleFiles : function(files) {
      var filePath = $("#dataupload").val();
          ext = filePath.substring(filePath.lastIndexOf('.') + 1).toLowerCase();
      if (ext != "csv" && ext != "xls" && ext != "xlsx") {
        $("#clearUpload").click();
        $(".data-upload label").css({"color": "#600", "font-weight":"bold"});
      } else {
        $("#clearUpload").fadeIn();
        $(".data-upload p").slideDown();
        var reader = new FileReader();
        reader.onload = function(file) {
          $.statlas.dataupload = file.currentTarget.result;
        };
        reader.readAsDataURL(files[0]);
      }

    },
    loading: function (text, delay) {
      text = text || "Loading...";
      delay = delay || 500;
      $("#loading").remove();
      $("<div id='loading'>").text(text).appendTo("body").fadeIn(delay);
    },
    doneLoading: function () {
      $("#loading").stop().fadeOut(500, function () {
        $(this).remove();
      });
    },
    setLink: function(slug) {
      var txt = $("#sharelink"),
          href = "http://statlas.nl/map/" + slug + "/",
          text = "statlas.nl/map/" + slug + "/";

      txt.fadeOut(100, function () {
        if(slug != "empty" && $("#id_public").is(":checked")) {
          txt.find("a").text(text).attr("href", href).end().fadeIn(100);
        }

      });

    },
    normaliseString: function (str) {
      return str.toLowerCase();
    },

    oc: function(a) {
      var o = {};
      for(var i=0;i<a.length;i++)
      {
        o[a[i]]='';
      }
      return o;
    }
  });

  $.maps = $.maps || {};
  $.extend($.maps, {
    //init function for maps
    init: function (id) {
    var po = org.polymaps,
        map = po.map(),
        container = $("#"+id),
        that = this,
        loadwrapper;
    that.po = po;
    that.map = map;


    //load map
    map.container(document.getElementById(id).appendChild(po.svg("svg")))
        .center({lat: 52.194, lon: 5.3})
        .zoom(7.4)
        .add(po.drag())
        .add(po.wheel())
        .add(po.dblclick())
        .add(po.hash());


    //background
    map.add(po.image()
        .url(po.url("http://{S}tile.cloudmade.com"
        + "/1a1b06b230af4efdbb989ea99e9841af" // http://cloudmade.com/register
        + "/17478/256/{Z}/{X}/{Y}.png")
        .hosts(["a.", "b.", "c.", ""])));
  },
  loadGeoJson: function(regioset, callback) {
    var id = "map1",
        that = this,
        po = org.polymaps;

    loadwrapper = function(e) {
      $(document.activeElement).blur();
      that.load(e, that, id, callback);
    };
    $.maplayers[id] = this.geoJsonLayer = this.po.geoJson()
      .url("/jsdata/regionsets/"+ regioset +".json").on("load",loadwrapper)
      .tile(false);
    this.map.add(this.geoJsonLayer);

    //add compass
    var zoom;
    if($("body").hasClass("embed")) {
      zoom = "small";
    } else {
      zoom = "big";
    }
    this.map.add(po.compass().position("top-right").pan("none").zoom(zoom));

  },
  load: function load(e, context, id, callback) {
    var that = context;
    $.statlas.loading("Loading...", 10);
    that.mapelement = e;
    $.statlas.regioList = [];
    for (var i = 0; i < e.features.length; i++) {
      var feature = e.features[i];

      var obj = {};
      obj.cityName = feature.data.properties.cityName;
      obj.citySlug = feature.data.properties.citySlug;
      $.statlas.regioList.push(obj);

      $(feature.element).attr("data-value", obj.cityName);
      $(feature.element).attr("name", obj.citySlug);

      // style elem
      $(feature.element)
        .tipsy({
          title:function () {return $(this).attr("data-value");},
          fallback: "onbekend",
          fade:true,
          html:true,
          gravity: "w"
        }).bind("click", function () {
          clearTimeout(window.blinkTimeout);
          $("#"+ $(this).attr("name")).focus();
        }).css({"cursor":"pointer"});
      //focus on first
      if(i==0) {
        var lat = feature.data.geometry.coordinates[0][0][0][1],
            lon = feature.data.geometry.coordinates[0][0][0][0];
        if (lat != undefined && lon != undefined) {
          that.map.center({
            lat: lat,
            lon: lon
          });
        }
      }
    }

    //set color!
    that.setColors($.statlas.valobject);

    //done loading
    $.statlas.doneLoading();

    //do callback
    if(!$.statlas.noInitCallback) {
      $.statlas.noInitCallback = true;
      callback();
    }


  },
  setColors: function(valobject) {
    var that = this,
        feature, i, val,
        e = that.mapelement;

    for (i = 0; i < e.features.length; i++) {
      feature = e.features[i];
      val = (valobject && valobject[feature.data.properties.citySlug]) || "rgba(0,40,0,0.1)";
      that.setColor(feature.data.properties.citySlug, val);
    }
  },
  setColor: function(el, val) {
    var that = this;
    el = $("path[name=" + el + "]");
    if( el.length>0 ) // Make sure we have selected an element, for the element might not exist yet
    {
      if (isNaN(val)) {
        if(val.startsWith("#") || val.startsWith("rgb") || val.startsWith("hsl") || (val in $.statlas.oc($.statlas.colorArray))) {
          //it's a color
          el.css("fill", val);
        } else if(that.checkname($.statlas.normaliseString(val)) in $.statlas.specialValues) {
          //special cases such as political parties
          el.css("fill", $.statlas.specialValues[that.checkname($.statlas.normaliseString(val))]);
        } else {
          //palette based
          el.css("fill", $.statlas.valcolors[val]);
        }
      } else {
        //percentage based filling
        perc = parseInt( (val-$.statlas.minvalue) / ($.statlas.maxvalue - $.statlas.minvalue) * 100, 10);
        fillperc = "rgba(" + perc + "," + perc*2 + ","+ perc + ", 1)";
        $(el).css("fill", fillperc);
      }

      if(!val) {
        el.css("fill", "rgba(0,40,0,0.1)");
      }

      if (val && val != "rgba(0,40,0,0.1)" && $(el).attr("data-value")) {
        newhover = $(el).attr("data-value").split(" <em>")[0] + " <em>(" + val + ")</em>";
      } else {
        newhover = $(el).attr("data-value").split(" <em>")[0];
      }
      $(el).attr("data-value", newhover);
    }
  },
  checkname: function (val) {
    for(i in $.statlas.specialNameValues) {
      for(j in $.statlas.specialNameValues[i]) {
        if (val == $.statlas.specialNameValues[i][j]) {
          return i;
        }
      }
    }
    return false;
  }
});

})(jQuery);


//python convenience funcs
String.prototype.startsWith = function(str) {return (this.match("^"+str)==str);}

String.prototype.endsWith = function(str) {return (this.match(str+"$")==str);}

String.prototype.trim = function(){ return (this.replace(/^[\s\xA0]+/, "").replace(/[\s\xA0]+$/, ""));}

//special cases
$.statlas.specialNameValues = {
  "cda": ["cda", "christen democratisch appel"],
  "pvda": ["pvda", "partij van de arbeid", "p v/d a", "p vd a"],
  "vvd": ["vvd", "volkspartij voor vrijheid en democratie"],
  "d66": ["d66", "democraten 66"],
  "groenlinks": ["groenlinks", "gl"],
  "sp": ["sp", "socialistische partij"],
  "pvv": ["pvv", "partij voor de vrijheid"],
  "cu-sgp": ["cu-sgp", "christenunie/sgp", "christenunie en sgp", "christenunie & sgp",],
  "cu": ["cu", "christenunie"],
  "sgp": ["sgp", "staatkundig gereformeerde partij"],
  "lpf": ["lpf", "lijst pim fortuyn"],
  "gpv": ["gpv", "gereformeerd politiek verbond"]
};

$.statlas.specialValues = {
  "cda": "rgb(254,119,12)",
  "pvda": "rgb(228, 6, 45)",
  "vvd": "rgb(13, 29, 111)",
  "d66": "rgb(254, 254, 0)",
  "groenlinks": "rgb(149, 197, 64)",
  "sp": "rgb(128, 0, 128)",
  "pvv": "rgb(150, 75, 0)",
  "cu-sgp": "rgb(125, 125, 125)",
  "cu": "rgb(175, 175, 175)",
  "sgp": "rgb(100, 100, 100)",
  "lpf": "rgb(175, 100, 0)",
  "gpv": "rgb(175, 175, 175)"
};

//all known color keywords plus function for checker
$.statlas.colorArray = [
"aliceblue",
"antiquewhite",
"aqua",
"aquamarine",
"azure",
"beige",
"bisque",
"black",
"blanchedalmond",
"blue",
"blueviolet",
"brown",
"burlywood",
"cadetblue",
"chartreuse",
"chocolate",
"coral",
"cornflowerblue",
"cornsilk",
"crimson",
"cyan",
"darkblue",
"darkcyan",
"darkgoldenrod",
"darkgray",
"darkgreen",
"darkgrey",
"darkkhaki",
"darkmagenta",
"darkolivegreen",
"darkorange",
"darkorchid",
"darkred",
"darksalmon",
"darkseagreen",
"darkslateblue",
"darkslategray",
"darkslategrey",
"darkturquoise",
"darkviolet",
"deeppink",
"deepskyblue",
"dimgray",
"dimgrey",
"dodgerblue",
"firebrick",
"floralwhite",
"forestgreen",
"fuchsia",
"gainsboro",
"ghostwhite",
"gold",
"goldenrod",
"gray",
"green",
"greenyellow",
"grey",
"honeydew",
"hotpink",
"indianred",
"indigo",
"ivory",
"khaki",
"lavender",
"lavenderblush",
"lawngreen",
"lemonchiffon",
"lightblue",
"lightcoral",
"lightcyan",
"lightgoldenrodyellow",
"lightgray",
"lightgreen",
"lightgrey",
"lightpink",
"lightsalmon",
"lightseagreen",
"lightskyblue",
"lightslategray",
"lightslategrey",
"lightsteelblue",
"lightyellow",
"lime",
"limegreen",
"linen",
"magenta",
"maroon",
"mediumaquamarine",
"mediumblue",
"mediumorchid",
"mediumpurple",
"mediumseagreen",
"mediumslateblue",
"mediumspringgreen",
"mediumturquoise",
"mediumvioletred",
"midnightblue",
"mintcream",
"mistyrose",
"mocc"
];

