/**
 * Salon Flow Owner Dashboard - Design System Types
 * Professional salon-appropriate design tokens and component variants
 */

// ============================================
// Color System
// ============================================
export type ColorVariant = 
  | 'primary' 
  | 'secondary' 
  | 'accent' 
  | 'success' 
  | 'warning' 
  | 'error' 
  | 'surface';

export type ColorShade = 50 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 950;

export interface ColorToken {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;
  600: string;
  700: string;
  800: string;
  900: string;
  950: string;
}

// ============================================
// Typography System
// ============================================
export type FontFamily = 'sans' | 'display' | 'mono';

export type FontSize = 
  | '2xs' 
  | 'xs' 
  | 'sm' 
  | 'base' 
  | 'lg' 
  | 'xl' 
  | '2xl' 
  | '3xl' 
  | '4xl' 
  | '5xl' 
  | '6xl';

export type FontWeight = 
  | 'thin'
  | 'extralight'
  | 'light'
  | 'normal'
  | 'medium'
  | 'semibold'
  | 'bold'
  | 'extrabold'
  | 'black';

export type LineHeight = 'none' | 'tight' | 'snug' | 'normal' | 'relaxed' | 'loose';

export interface TypographyStyle {
  fontFamily?: FontFamily;
  fontSize: FontSize;
  fontWeight?: FontWeight;
  lineHeight?: LineHeight;
  letterSpacing?: 'tighter' | 'tight' | 'normal' | 'wide' | 'wider' | 'widest';
}

// ============================================
// Spacing System
// ============================================
export type Spacing = 
  | 0 | 0.5 | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 5 
  | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 14 | 16 | 20 
  | 24 | 28 | 32 | 36 | 40 | 44 | 48 | 52 | 56 | 60 
  | 64 | 72 | 80 | 96 | 'px' | 'auto';

// ============================================
// Border System
// ============================================
export type BorderWidth = 0 | 1 | 2 | 4 | 8;

export type BorderStyle = 'solid' | 'dashed' | 'dotted' | 'double' | 'none';

export type BorderRadius = 
  | 'none' 
  | 'sm' 
  | 'DEFAULT' 
  | 'md' 
  | 'lg' 
  | 'xl' 
  | '2xl' 
  | '3xl' 
  | '4xl' 
  | '5xl' 
  | 'full';

// ============================================
// Shadow System
// ============================================
export type ShadowVariant = 
  | 'none' 
  | 'sm' 
  | 'DEFAULT' 
  | 'md' 
  | 'lg' 
  | 'xl' 
  | '2xl' 
  | 'inner' 
  | 'soft' 
  | 'card' 
  | 'card-hover' 
  | 'glow';

// ============================================
// Component Variants
// ============================================
export type ButtonVariant = 
  | 'primary' 
  | 'secondary' 
  | 'accent' 
  | 'outline' 
  | 'ghost' 
  | 'link' 
  | 'danger' 
  | 'success';

export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export type InputSize = 'sm' | 'md' | 'lg';

export type InputVariant = 'default' | 'filled' | 'flushed' | 'unstyled';

export type CardVariant = 'default' | 'elevated' | 'outlined' | 'filled';

export type BadgeVariant = 'default' | 'solid' | 'outline' | 'subtle' | 'success' | 'warning' | 'error' | 'info' | 'secondary';

export type BadgeColor = ColorVariant | 'gray' | 'info';

export type AlertVariant = 'solid' | 'subtle' | 'outline' | 'left-accent' | 'top-accent';

export type AlertStatus = 'success' | 'warning' | 'error' | 'info';

export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

export type ModalSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl' | 'full';

export type TooltipPlacement = 'top' | 'right' | 'bottom' | 'left' | 'auto';

// ============================================
// Layout Types
// ============================================
export type SidebarPosition = 'left' | 'right';

export type SidebarVariant = 'default' | 'compact' | 'mini';

export type HeaderVariant = 'default' | 'compact' | 'transparent';

export type ContainerSize = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';

export type GridColumns = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;

export type GridGap = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16 | 20 | 24;

// ============================================
// Responsive Types
// ============================================
export type Breakpoint = 'sm' | 'md' | 'lg' | 'xl' | '2xl';

export interface ResponsiveValue<T> {
  base?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  '2xl'?: T;
}

// ============================================
// Animation Types
// ============================================
export type AnimationType = 
  | 'fade-in' 
  | 'fade-in-up' 
  | 'fade-in-down' 
  | 'slide-in-right' 
  | 'slide-in-left' 
  | 'scale-in' 
  | 'spin-slow' 
  | 'pulse-soft' 
  | 'shimmer' 
  | 'bounce-soft';

export type TransitionDuration = '75' | '100' | '150' | '200' | '300' | '500' | '700' | '1000';

export type TransitionTiming = 'linear' | 'in' | 'out' | 'in-out' | 'bounce-in' | 'smooth';

// ============================================
// State Types
// ============================================
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export type InteractionState = 'default' | 'hover' | 'focus' | 'active' | 'disabled';

// ============================================
// Accessibility Types
// ============================================
export interface A11yProps {
  role?: string;
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-hidden'?: boolean;
  'aria-expanded'?: boolean;
  'aria-controls'?: string;
  'aria-haspopup'?: 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog';
  'aria-live'?: 'off' | 'polite' | 'assertive';
  'aria-atomic'?: boolean;
  'aria-relevant'?: 'additions' | 'removals' | 'text' | 'all';
  tabIndex?: number;
}

// ============================================
// Component Props Interfaces
// ============================================
export interface BaseComponentProps {
  id?: string;
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
  testId?: string;
}

export interface InteractiveComponentProps extends BaseComponentProps, A11yProps {
  disabled?: boolean;
  loading?: boolean;
  onClick?: (event: React.MouseEvent) => void;
  onFocus?: (event: React.FocusEvent) => void;
  onBlur?: (event: React.FocusEvent) => void;
}

// ============================================
// Theme Configuration
// ============================================
export interface ThemeConfig {
  colors: {
    primary: ColorToken;
    secondary: ColorToken;
    accent: ColorToken;
    success: ColorToken;
    warning: ColorToken;
    error: ColorToken;
    surface: ColorToken;
  };
  typography: {
    fontFamily: Record<FontFamily, string>;
    fontSize: Record<FontSize, [string, { lineHeight: string }]>;
  };
  spacing: Record<string, string>;
  borderRadius: Record<string, string>;
  shadows: Record<string, string>;
  transitions: {
    duration: Record<TransitionDuration, string>;
    timing: Record<TransitionTiming, string>;
  };
}

// ============================================
// Utility Types
// ============================================
export type WithRequired<T, K extends keyof T> = T & { [P in K]-?: T[P] };

export type WithOptional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type PolymorphicComponentProps<E extends React.ElementType, Props = object> = 
  React.PropsWithChildren<Props> & {
    as?: E;
  } & Omit<React.ComponentPropsWithoutRef<E>, 'as' | keyof Props>;

export type PolymorphicComponent<E extends React.ElementType, Props = object> = 
  React.ForwardRefExoticComponent<PolymorphicComponentProps<E, Props>>;

export type BookingStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed' | 'no-show' | 'in-progress';
