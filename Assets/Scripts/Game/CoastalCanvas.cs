using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;

namespace Catchline.Game
{
    // Retained native UI: shared sliced artwork, typography, input and capture.
    public sealed partial class CoastalCanvas : MonoBehaviour
    {
        sealed class Element
        {
            public RectTransform Rect;
            public Image Image;
            public Text Text;
            public Button Button;
            public Action Action;
            public bool Used;
        }
        readonly Dictionary<string, Element> elements = new();
        readonly Dictionary<string, Sprite> sprites = new();
        Canvas canvas;
        Camera sceneCamera;
        public RectTransform Root { get; private set; }
        public float Width, Height;
        public float TypeScale = 1;
        Font font;
        Font referenceRegular, referenceBold;
        public float ReferenceScale { get; set; } = 1;

        public static CoastalCanvas Create(Transform parent, Camera camera)
        {
            var go = new GameObject("Catchline coastal interface", typeof(RectTransform), typeof(Canvas), typeof(GraphicRaycaster));
            go.transform.SetParent(parent, false);
            var ui = go.AddComponent<CoastalCanvas>();
            var safe = new GameObject("Safe area", typeof(RectTransform));
            safe.transform.SetParent(go.transform, false);
            ui.Root = (RectTransform)safe.transform;
            ui.canvas = go.GetComponent<Canvas>();
            ui.canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            ui.sceneCamera = camera;
            camera.cullingMask &= ~(1 << 5);
            ui.canvas.worldCamera = camera;
            ui.canvas.planeDistance = .5f;
            ui.canvas.sortingOrder = 20;
            ui.canvas.pixelPerfect = true;
            ui.font = ArtLibrary.Get()?.UiFont;
            go.layer = safe.layer = 5;
            if (EventSystem.current == null)
            {
                var events = new GameObject("Coastal UI input", typeof(EventSystem), typeof(InputSystemUIInputModule));
                events.transform.SetParent(parent, false);
                events.GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
            }
            return ui;
        }

        public void Begin(int width, int height, float typeScale, Rect safeArea)
        {
            canvas.enabled = true;
            TypeScale = typeScale;
            if (safeArea.width <= 0 || safeArea.height <= 0) safeArea = new Rect(0, 0, width, height);
            Height = safeArea.height < 600 ? 480 : 720;
            canvas.scaleFactor = safeArea.height / Height;
            Width = safeArea.width / canvas.scaleFactor;
            // Safe-area root; children use logical top-left coordinates.
            Root.anchorMin = new Vector2(safeArea.x / width, safeArea.y / height);
            Root.anchorMax = new Vector2(safeArea.xMax / width, safeArea.yMax / height);
            Root.offsetMin = Vector2.zero; Root.offsetMax = Vector2.zero;
            foreach (var e in elements.Values) e.Used = false;
            bubbles.Clear(); BubbleTop = BubbleLeft = 12; BubbleRight = BubbleBottom = 0;
        }
        public void Hide() { if (canvas != null) canvas.enabled = false; }
        public void RenderCapture(RenderTexture target)
        {
            // Capture the same production Canvas, bypassing scene tonemapping.
            var cameraData = sceneCamera.GetComponent<UnityEngine.Rendering.Universal.UniversalAdditionalCameraData>();
            int mask = sceneCamera.cullingMask;
            var flags = sceneCamera.clearFlags; var background = sceneCamera.backgroundColor;
            bool post = cameraData.renderPostProcessing;
            var previousTarget = sceneCamera.targetTexture;
            sceneCamera.cullingMask = 1 << 5;
            sceneCamera.clearFlags = CameraClearFlags.SolidColor; sceneCamera.backgroundColor = Color.clear;
            cameraData.renderPostProcessing = false;
            canvas.renderMode = RenderMode.ScreenSpaceCamera;
            canvas.worldCamera = sceneCamera;
            sceneCamera.targetTexture = target;
            canvas.enabled = false; canvas.enabled = true;
            Canvas.ForceUpdateCanvases();
            var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest { destination = target };
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(sceneCamera, request);
            sceneCamera.targetTexture = previousTarget;
            sceneCamera.cullingMask = mask; sceneCamera.clearFlags = flags; sceneCamera.backgroundColor = background;
            cameraData.renderPostProcessing = post;
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            Canvas.ForceUpdateCanvases();
        }
        public void End()
        {
            foreach (var e in elements.Values) if (!e.Used && e.Rect.gameObject.activeSelf) e.Rect.gameObject.SetActive(false);
        }
        Element Get(string id, Rect r, Transform parent = null)
        {
            if (!elements.TryGetValue(id, out var e))
            {
                var go = new GameObject(id, typeof(RectTransform));
                go.layer = 5;
                e = new Element { Rect = (RectTransform)go.transform };
                elements.Add(id, e);
            }
            e.Used = true;
            if (!e.Rect.gameObject.activeSelf) e.Rect.gameObject.SetActive(true);
            if (e.Rect.parent != (parent ?? Root)) e.Rect.SetParent(parent ?? Root, false);
            e.Rect.SetAsLastSibling();
            e.Rect.anchorMin = e.Rect.anchorMax = e.Rect.pivot = new Vector2(0, 1);
            e.Rect.anchoredPosition = new Vector2(r.x, -r.y);
            e.Rect.sizeDelta = r.size;
            return e;
        }
        Sprite Sprite(string name, bool sliced)
        {
            string key = name + (sliced ? ":slice" : "");
            if (sprites.TryGetValue(key, out var result)) return result;
            var texture = ArtLibrary.Get()?.UiTex(name);
            if (texture == null) return null;
            var spriteRect = GeminiUiSkin.SpriteRect(texture);
            bool trimmed = spriteRect.width != texture.width || spriteRect.height != texture.height;
            float edge = trimmed ? Mathf.Min(14, Mathf.Min(spriteRect.width, spriteRect.height) * .18f)
                : Mathf.Min(24, Mathf.Min(texture.width, texture.height) / 3f);
            result = UnityEngine.Sprite.Create(texture, spriteRect, Vector2.one * .5f,
                100, 0, SpriteMeshType.FullRect, sliced ? new Vector4(edge, edge, edge, edge) : Vector4.zero);
            result.name = name;
            sprites[key] = result;
            return result;
        }
        // Legacy kit names resolve to the UI v2 kit so every screen shares one skin while it is rebuilt.
        static string V2Equivalent(string art) => art switch
        {
            "panel-cream" or "popup-panel" => "v2-slab", "card-white" => "v2-card", "card-selected" => "v2-card-selected",
            "toast-dark" => "v2-pill-navy", "button-primary-normal" => "v2-btn-primary", "button-secondary-normal" => "v2-btn-secondary",
            "button-tab-on-normal" => "v2-tab-on", "button-tab-off-normal" => "v2-tab-off", "button-disabled-normal" => "v2-btn-disabled",
            "bubble-white" => "v2-bubble", "bubble-hot" => "v2-bubble-hot", _ => null
        };
        public RectTransform Box(string id, Rect r, string art = "panel-cream", Color? tint = null, Transform parent = null, bool blocks = true)
        {
            if (V2Equivalent(art) is string v2) return Sliced(id, r, v2, parent, tint, blocks);
            var e = Get(id, r, parent);
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<Image>();
            e.Image.sprite = Sprite(art, true);
            e.Image.type = e.Image.sprite != null ? Image.Type.Sliced : Image.Type.Simple;
            e.Image.preserveAspect = false;
            e.Image.color = tint ?? Skin.Paper;
            e.Image.raycastTarget = blocks;
            return e.Rect;
        }
        public void Art(string id, Rect r, string art, Transform parent = null, Color? tint = null)
        {
            var e = Get(id, r, parent);
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<Image>();
            e.Image.sprite = Sprite(art, false); e.Image.type = Image.Type.Simple;
            e.Image.preserveAspect = true; e.Image.color = tint ?? Color.white; e.Image.raycastTarget = false;
        }
        public RectTransform ResourceArt(string id, Rect r, string resource, bool stretch = false, Transform parent = null)
        {
            string key = "resource:" + resource;
            if (!sprites.TryGetValue(key, out var sprite))
            {
                var texture = Resources.Load<Texture2D>(resource);
                if (texture != null) sprite = UnityEngine.Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), Vector2.one * .5f, 100);
                sprites[key] = sprite;
            }
            var e = Get(id, r, parent);
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<Image>();
            e.Image.sprite = sprite; e.Image.type = Image.Type.Simple;
            e.Image.preserveAspect = !stretch; e.Image.color = Color.white; e.Image.raycastTarget = false;
            return e.Rect;
        }
        Text ClippedText(Element e, string id)
        {
            if (e.Text != null) return e.Text;
            // RectMask2D deliberately ignores a Graphic on its own object in UGUI.
            // Keep the mask on the retained outer rect and the text in a stretched child.
            e.Rect.name = id + "/clip";
            if (e.Rect.GetComponent<RectMask2D>() == null) e.Rect.gameObject.AddComponent<RectMask2D>();
            var child = new GameObject(id, typeof(RectTransform), typeof(CanvasRenderer), typeof(Text));
            child.layer = 5; var rect = (RectTransform)child.transform;
            rect.SetParent(e.Rect, false); rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one;
            rect.offsetMin = rect.offsetMax = Vector2.zero;
            e.Text = child.GetComponent<Text>(); return e.Text;
        }
        public void Label(string id, Rect r, string value, int size = 18, Color? color = null,
            TextAnchor align = TextAnchor.MiddleLeft, Transform parent = null, bool fitted = false)
        {
            var e = Get(id, r, parent);
            if (fitted) ClippedText(e, id);
            else if (e.Text == null) e.Text = e.Rect.gameObject.AddComponent<Text>();
            e.Text.font = BodyOverride != null ? BodyOverride : font;
            e.Text.fontSize = Mathf.RoundToInt(size * TypeScale);
            e.Text.resizeTextForBestFit = fitted;
            e.Text.resizeTextMaxSize = e.Text.fontSize;
            e.Text.resizeTextMinSize = Mathf.Min(e.Text.fontSize, Mathf.Max(10, Mathf.RoundToInt(size * .72f)));
            e.Text.color = color ?? Palette.HullNavy;
            e.Text.alignment = align; e.Text.supportRichText = true;
            e.Text.horizontalOverflow = HorizontalWrapMode.Wrap;
            e.Text.verticalOverflow = VerticalWrapMode.Truncate;
            e.Text.raycastTarget = false;
            if (e.Text.text != value) e.Text.text = value;
        }
        public void Button(string id, Rect r, string label, Action action, string art = "button-primary-normal",
            bool enabled = true, Transform parent = null, int size = 18)
        {
            if (art == "button-primary-normal") { Primary(id, r, label, action, null, enabled, parent); return; }
            if (art == "button-secondary-normal") { Secondary(id, r, label, action, null, enabled, parent); return; }
            Box(id, r, enabled ? art : "button-disabled-normal", null, parent);
            var e = elements[id];
            if (e.Button == null)
            {
                e.Button = e.Rect.gameObject.AddComponent<Button>();
                e.Button.targetGraphic = e.Image;
                e.Button.onClick.AddListener(() => e.Action?.Invoke());
                var colors = e.Button.colors;
                colors.highlightedColor = new Color(1, 1, .94f); colors.pressedColor = new Color(.85f, .9f, .9f);
                colors.disabledColor = Color.white;
                e.Button.colors = colors;
            }
            e.Button.interactable = enabled; e.Action = enabled ? action : null;
            Label(id + "/caption", new Rect(10, 0, r.width - 20, r.height - 4), label, size,
                enabled && art.Contains("secondary") || art.Contains("tab-on") ? Palette.Cream : Palette.HullNavy,
                TextAnchor.MiddleCenter, e.Rect);
        }
        public void Bar(string id, Rect r, float progress, bool warning = false, Transform parent = null)
        {
            if (V2("v2-bar-track") != null) { ProgressBar(id, r, progress, warning ? Skin.Bar.Bad : Skin.Bar.Teal, parent); return; }
            Box(id, r, "bar-background", null, parent, false);
            if (progress > .001f) Box(id + "/fill", new Rect(r.x, r.y, Mathf.Max(5, r.width * Mathf.Clamp01(progress)), r.height),
                warning ? "bar-red" : "bar-teal", null, parent, false);
        }
        public RectTransform Scroll(string id, Rect r, float contentHeight)
        {
            var e = Get(id, r);
            var mask = e.Rect.GetComponent<RectMask2D>();
            if (mask == null) e.Rect.gameObject.AddComponent<RectMask2D>();
            var scroller = e.Rect.GetComponent<ScrollRect>();
            Vector2 offset = scroller != null && scroller.content != null ? scroller.content.anchoredPosition : Vector2.zero;
            if (scroller == null)
            {
                scroller = e.Rect.gameObject.AddComponent<ScrollRect>();
                scroller.horizontal = false; scroller.vertical = true;
                scroller.movementType = ScrollRect.MovementType.Clamped; scroller.scrollSensitivity = 35;
            }
            Box(id + "/hit", new Rect(0, 0, r.width, r.height), "", new Color(0, 0, 0, .001f), e.Rect);
            var content = Get(id + "/content", new Rect(0, 0, r.width - 12, Mathf.Max(r.height, contentHeight)), e.Rect);
            // Preserve drag/wheel position while the retained content updates.
            scroller.viewport = e.Rect; scroller.content = content.Rect;
            content.Rect.anchoredPosition = new Vector2(0, Mathf.Clamp(offset.y, 0, Mathf.Max(0, contentHeight - r.height)));
            var track = Box(id + "/track", new Rect(r.width - 8, 0, 8, r.height), "bar-background", null, e.Rect);
            var thumb = Box(id + "/thumb", new Rect(0, 0, 8, 48), "bar-teal", null, track);
            var scrollbar = track.GetComponent<Scrollbar>();
            if (scrollbar == null)
            {
                scrollbar = track.gameObject.AddComponent<Scrollbar>();
                scrollbar.direction = Scrollbar.Direction.BottomToTop;
                scrollbar.handleRect = thumb; scrollbar.targetGraphic = thumb.GetComponent<Image>();
                scrollbar.SetValueWithoutNotify(1);
            }
            thumb.sizeDelta = Vector2.zero;
            scrollbar.Rebuild(CanvasUpdate.PreRender);
            scroller.verticalScrollbar = scrollbar;
            return content.Rect;
        }
        Sprite ReferenceSprite(string asset, bool sliced = false, float border = 12)
        {
            string key = "reference/" + asset + (sliced ? ":" + border : "");
            if (sprites.TryGetValue(key, out var sprite)) return sprite;
            var texture = Resources.Load<Texture2D>("FishReference/" + asset);
            if (texture == null)
            {
                Debug.LogWarning("[Catchline] Missing reference HUD resource FishReference/" + asset + ". Copy the FishReference Resources dependency into the test project.");
                sprites[key] = null;
                return null;
            }
            sprite = UnityEngine.Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height),
                Vector2.one * .5f, 100, 0, SpriteMeshType.FullRect,
                sliced ? new Vector4(border, border, border, border) : Vector4.zero);
            sprite.name = key;
            sprites[key] = sprite;
            return sprite;
        }
        void ReferenceImage(string id, Rect r, string asset, bool sliced = false, float border = 12, bool blocks = false)
        {
            var e = Get(id, r);
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<Image>();
            e.Image.sprite = ReferenceSprite(asset, sliced, border);
            e.Image.type = sliced ? Image.Type.Sliced : Image.Type.Simple;
            e.Image.pixelsPerUnitMultiplier = 1 / Mathf.Max(.001f, ReferenceScale);
            e.Image.preserveAspect = false;
            e.Image.color = Color.white;
            e.Image.raycastTarget = blocks;
        }
        public void ReferencePanel(string id, Rect r, FishReferenceStyle.PanelKind kind, Color? tint = null)
        {
            // Original perimeter and cream pixels; content cleared mechanically from source.
            ReferenceImage(id, r, FishReferenceStyle.Panel(kind), kind != FishReferenceStyle.PanelKind.Status, 16, true);
            if (tint.HasValue) elements[id].Image.color = tint.Value;
        }
        public void ReferenceIcon(string id, Rect r, FishReferenceStyle.Icon icon) =>
            ReferenceImage(id, r, FishReferenceStyle.IconName(icon));
        public void ReferencePortrait(string id, Rect r, string role) =>
            ReferenceImage(id, r, "portrait-" + role);
        public void ReferenceLabel(string id, Rect r, string value, float referencePixelSize,
            bool bold = false, TextAnchor align = TextAnchor.MiddleLeft, bool useCaption = true)
        {
            // Static headings retain original raster lettering rather than guessing the font.
            string caption = useCaption && bold && Mathf.Approximately(TypeScale, 1) ? FishReferenceStyle.Caption(value) : null;
            if (caption != null)
            {
                var sprite = ReferenceSprite(caption);
                if (sprite != null)
                {
                    float h = sprite.rect.height * ReferenceScale;
                    float w = sprite.rect.width * ReferenceScale;
                    float x = align == TextAnchor.MiddleCenter ? r.center.x - w / 2 : r.x;
                    float offset = value == "Crew" ? 2 : value == "Current Goal" ? 1 : 0;
                    ReferenceImage(id + "/raster", new Rect(x, r.y + offset * ReferenceScale, w, h), caption);
                    return;
                }
            }
            if (referenceRegular == null) referenceRegular = Resources.Load<Font>("FishReference/ReferenceRegular");
            if (referenceBold == null) referenceBold = Resources.Load<Font>("FishReference/ReferenceBold");
            var e = Get(id, r);
            if (e.Text == null) e.Text = e.Rect.gameObject.AddComponent<Text>();
            e.Text.font = (bold ? referenceBold : referenceRegular) ?? font;
            e.Text.fontSize = Mathf.Max(1, Mathf.RoundToInt(referencePixelSize * ReferenceScale * TypeScale));
            e.Text.color = id == "reference/status/coins" ? FishReferenceStyle.AmountInk : bold ? FishReferenceStyle.Ink : FishReferenceStyle.Secondary;
            e.Text.alignment = align; e.Text.supportRichText = false;
            e.Text.horizontalOverflow = HorizontalWrapMode.Wrap;
            e.Text.verticalOverflow = VerticalWrapMode.Truncate;
            e.Text.resizeTextForBestFit = true;
            e.Text.resizeTextMaxSize = e.Text.fontSize;
            e.Text.resizeTextMinSize = Mathf.Max(1, Mathf.RoundToInt(e.Text.fontSize * .72f));
            e.Text.raycastTarget = false;
            if (e.Text.text != value) e.Text.text = value;
        }
        public void ReferenceBar(string id, Rect r, float progress)
        {
            ReferenceImage(id, r, "bar-track", true, 6);
            progress = Mathf.Clamp01(progress);
            if (progress > 0)
            {
                ReferenceImage(id + "/fill", new Rect(r.x, r.y, r.width * progress, r.height), "bar-fill", true, 6);
            }
        }
        public Rect ReferenceButton(string id, Rect r, System.Action action)
        {
            // Expand only the invisible hit area to 44 points; keep source artwork exact.
            float target = TouchPixels / Mathf.Max(.001f, canvas.scaleFactor);
            r = new Rect(r.center.x - Mathf.Max(target, r.width) / 2, r.center.y - Mathf.Max(target, r.height) / 2,
                Mathf.Max(target, r.width), Mathf.Max(target, r.height));
            r.x = Mathf.Clamp(r.x, 0, Mathf.Max(0, Width - r.width));
            r.y = Mathf.Clamp(r.y, 0, Mathf.Max(0, Height - r.height));
            var e = Get(id, r);
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<Image>();
            e.Image.sprite = null; e.Image.color = new Color(1, 1, 1, 0); e.Image.raycastTarget = true;
            if (e.Button == null)
            {
                e.Button = e.Rect.gameObject.AddComponent<Button>();
                e.Button.targetGraphic = e.Image;
                e.Button.onClick.AddListener(() => e.Action?.Invoke());
            }
            e.Action = action; e.Button.interactable = action != null;
            return r;
        }
        readonly Dictionary<string, Texture2D> dashboardTextures = new();
        Font dashboardRegular,dashboardBold;
        public void DashboardRegion(string id,Rect r,string asset,Rect source)
        {
            if(!dashboardTextures.TryGetValue(asset,out var texture))
            { texture=Resources.Load<Texture2D>("ManagementReference/"+asset);dashboardTextures[asset]=texture; }
            var e=Get(id,r);var raw=e.Rect.GetComponent<RawImage>()??e.Rect.gameObject.AddComponent<RawImage>();
            raw.texture=texture;raw.color=Color.white;raw.raycastTarget=false;
            raw.uvRect=new Rect(source.x/1672,1-source.yMax/941,source.width/1672,source.height/941);
        }
        public void DashboardText(string id,Rect r,string value,float size,Color color,bool bold=false,TextAnchor align=TextAnchor.MiddleLeft)
        {
            if(dashboardRegular==null)dashboardRegular=Resources.Load<Font>("ManagementReference/DashboardRegular");
            if(dashboardBold==null)dashboardBold=Resources.Load<Font>("ManagementReference/DashboardBold");
            var e=Get(id,r);if(e.Text==null)e.Text=e.Rect.gameObject.AddComponent<Text>();
            e.Text.font=(bold?dashboardBold:dashboardRegular)??font;e.Text.fontSize=Mathf.Max(1,Mathf.RoundToInt(size));
            e.Text.color=color;e.Text.alignment=align;e.Text.supportRichText=true;e.Text.raycastTarget=false;
            e.Text.horizontalOverflow=HorizontalWrapMode.Wrap;e.Text.verticalOverflow=VerticalWrapMode.Truncate;
            e.Text.resizeTextForBestFit=true;e.Text.resizeTextMaxSize=e.Text.fontSize;e.Text.resizeTextMinSize=Mathf.Max(1,Mathf.RoundToInt(size*.72f));
            if(e.Text.text!=value)e.Text.text=value;
        }
        public void DashboardShape(string id,Rect r,Color color,float fraction=1,bool ring=false)
        {
            var e=Get(id,r);var shape=e.Rect.GetComponent<DashboardGeometry>()??e.Rect.gameObject.AddComponent<DashboardGeometry>();
            shape.raycastTarget=false;shape.Set(color,fraction,ring,null);
        }
        public void DashboardPlot(string id,Rect r,Color color,Vector2[] points)
        {
            var e=Get(id,r);var shape=e.Rect.GetComponent<DashboardGeometry>()??e.Rect.gameObject.AddComponent<DashboardGeometry>();
            shape.raycastTarget=false;shape.Set(color,1,false,points);
        }
        public bool Invoke(string id)
        {
            if (!elements.ContainsKey(id) && aliases.TryGetValue(id, out var target)) id = target;
            if (!elements.TryGetValue(id, out var e) || e.Button == null || !e.Button.interactable || !e.Used) return false;
            e.Button.onClick.Invoke(); return true;
        }
        void OnDestroy() { foreach (var sprite in sprites.Values) if (sprite != null) Prototype.Visuals.Kill(sprite); }
    }
    // Native UGUI geometry: round bars, chart strokes and a real data-driven donut.
    public sealed class DashboardGeometry : MaskableGraphic
    {
        float fraction=1;bool ring;Vector2[] points;
        public void Set(Color tint,float fill,bool isRing,Vector2[] samples)
        { if(color!=tint||fraction!=fill||ring!=isRing||samples!=null||points!=null){color=tint;fraction=fill;ring=isRing;points=samples;SetVerticesDirty();} }
        void Quad(VertexHelper vh,Vector2 a,Vector2 b,Vector2 c,Vector2 d)
        {int n=vh.currentVertCount;vh.AddVert(a,color,Vector2.zero);vh.AddVert(b,color,Vector2.zero);vh.AddVert(c,color,Vector2.zero);vh.AddVert(d,color,Vector2.zero);vh.AddTriangle(n,n+1,n+2);vh.AddTriangle(n,n+2,n+3);}
        void Disc(VertexHelper vh,Vector2 center,float radius)
        {for(int n=0;n<16;n++){float a=n*Mathf.PI/8,b=(n+1)*Mathf.PI/8;Quad(vh,center,center+new Vector2(Mathf.Cos(a),Mathf.Sin(a))*radius,center+new Vector2(Mathf.Cos(b),Mathf.Sin(b))*radius,center);}}
        protected override void OnPopulateMesh(VertexHelper vh)
        {
            vh.Clear();var r=rectTransform.rect;float w=r.width,h=r.height;
            if(points!=null)
            {
                float width=Mathf.Max(1.3f,h*.025f);
                Vector2 P(Vector2 p)=>new(r.x+p.x*w,r.y+p.y*h);
                for(int n=1;n<points.Length;n++)
                {var a=P(points[n-1]);var b=P(points[n]);var normal=new Vector2(-(b-a).y,(b-a).x).normalized*width/2;Quad(vh,a+normal,b+normal,b-normal,a-normal);}
                foreach(var p in points)Disc(vh,P(p),width*1.35f);
                return;
            }
            if(ring)
            {
                var center=r.center;float outer=Mathf.Min(w,h)/2,inner=outer*.78f;int segments=Mathf.CeilToInt(120*Mathf.Clamp01(fraction));
                for(int n=0;n<segments;n++){float a=Mathf.PI/2-n/120f*Mathf.PI*2,b=Mathf.PI/2-Mathf.Min((n+1)/120f,fraction)*Mathf.PI*2;var u=new Vector2(Mathf.Cos(a),Mathf.Sin(a));var v=new Vector2(Mathf.Cos(b),Mathf.Sin(b));Quad(vh,center+u*outer,center+v*outer,center+v*inner,center+u*inner);}
                return;
            }
            w*=Mathf.Clamp01(fraction);if(w<=0)return;float radius=Mathf.Min(h/2,w/2);var left=new Vector2(r.x+radius,r.y+h/2);var right=new Vector2(r.x+w-radius,r.y+h/2);
            Quad(vh,new Vector2(left.x,r.y),new Vector2(right.x,r.y),new Vector2(right.x,r.y+h),new Vector2(left.x,r.y+h));Disc(vh,left,radius);Disc(vh,right,radius);
        }
    }

}
